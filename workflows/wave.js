export const meta = {
  name: 'kit-wave',
  description: 'backend-agent-kit wave: one worker per task, an anchor that re-runs check, fresh reviewers per task, fan-in guard, structured result for the coordinator to integrate',
  whenToUse: 'Running a wave of independent tasks from a phase ledger in a project built with the backend-agent-kit. The coordinator scouts the ledger, resolves decisions and claims tasks first, then passes them as args.',
  phases: [
    { title: 'Build', detail: 'one kit-worker per task, in its own copy or worktree' },
    { title: 'Anchor', detail: 'a fresh agent re-runs the check command on each result; the worker\'s claim is not the evidence' },
    { title: 'Review', detail: 'fresh reviewers per task; three lenses with majority for heavy change types' },
  ],
}

// ---------------------------------------------------------------------------------------------
// args (built by the coordinator after Stage 0 and Stage 1 of sdlc-workflow; nothing is read here):
// {
//   repo: '/abs/path/to/repo', scratch: '/abs/path/to/scratchpad/waveN',
//   isolation: 'copy' | 'worktree',                 // the project's isolation ADR
//   stack: { check: 'make check', deps_sync: 'make sync' },   // from project-guide/knowledge/STACK.md
//   max_agents: 4,                                   // workers launched at once; the rest are reported as not launched
//   heavy_types: ['feature','schema','runtime','interface','security-sensitive'],
//   agent_types: { worker: 'backend-agent-kit:kit-worker', reviewer: 'backend-agent-kit:kit-reviewer', anchor: 'general-purpose' },
//   off_limits: 'dev database localhost:55432, compose volumes',
//   tasks: [{ id: 'P04-T2', title, change_type, goal, scope_in: [..], scope_out: [..], writable: [..],
//             read_first: [..], acceptance: [..], verify: [..], ports: '18120/18121', db: 'testcontainers' }]
// }
// ---------------------------------------------------------------------------------------------

const WORKER_REPORT = {
  type: 'object',
  required: ['task_id', 'status', 'summary', 'files_changed', 'verification', 'patches', 'needs_from_coordinator', 'deviations'],
  properties: {
    task_id: { type: 'string' },
    status: { type: 'string', enum: ['done', 'partial', 'blocked'] },
    summary: { type: 'string', description: 'Two or three sentences. Prose lives here and nowhere else.' },
    files_changed: { type: 'array', items: { type: 'object', required: ['path'], properties: { path: { type: 'string' }, lines: { type: 'integer' } } } },
    verification: { type: 'array', items: { type: 'object', required: ['command', 'exit_code'], properties: { command: { type: 'string' }, exit_code: { type: 'integer' }, passed: { type: 'integer' }, failed: { type: 'integer' } } } },
    change_record: { type: 'string', description: 'path of the change record in the copy or worktree' },
    patches: { type: 'object', properties: { main: { type: 'string' }, shared: { type: 'string' }, checkpoint: { type: 'string' } } },
    workspace: { type: 'string', description: 'absolute path of the copy or worktree the work is in' },
    ledger_row: { type: 'string' },
    index_row: { type: 'string' },
    needs_from_coordinator: { type: 'array', items: { type: 'string' } },
    decisions_needed: { type: 'array', items: { type: 'string' } },
    deviations: { type: 'array', items: { type: 'string' } },
  },
}

const ANCHOR = {
  type: 'object',
  required: ['command', 'exit_code', 'output_tail'],
  properties: {
    command: { type: 'string' },
    exit_code: { type: 'integer' },
    passed: { type: 'integer' },
    failed: { type: 'integer' },
    output_tail: { type: 'string', description: 'last 15 lines of real output' },
  },
}

const VERDICT = {
  type: 'object',
  required: ['lens', 'must_fix', 'should_fix', 'integrate_as_is'],
  properties: {
    lens: { type: 'string' },
    must_fix: { type: 'array', items: { type: 'object', required: ['where', 'issue', 'fix'], properties: { where: { type: 'string' }, issue: { type: 'string' }, fix: { type: 'string' } } } },
    should_fix: { type: 'array', items: { type: 'object', required: ['where', 'issue', 'fix'], properties: { where: { type: 'string' }, issue: { type: 'string' }, fix: { type: 'string' } } } },
    nits: { type: 'array', items: { type: 'string' } },
    integrate_as_is: { type: 'boolean' },
  },
}

const LENSES = {
  correctness: 'Correctness: does the diff do what the acceptance criteria say; edge cases; concurrency; idempotency; recorded intent for outside writes; typed failures; nothing swallowed.',
  invariants: 'Invariants and structure: INVARIANTS.md, layer direction, vendor isolation, registries not branches, vocabulary (no retired terms), shared-hot-file discipline, docs updated with the change.',
  tests: 'Tests: do the tests prove the behaviour at the right layer; a failing test preceded a bug fix; no weakened assertion; verification output is real and covers every suite the change type requires.',
}

const stack = args.stack || {}
const types = Object.assign({ worker: 'backend-agent-kit:kit-worker', reviewer: 'backend-agent-kit:kit-reviewer', anchor: 'general-purpose' }, args.agent_types || {})
const heavy = new Set(args.heavy_types || ['feature', 'schema', 'runtime', 'interface', 'security-sensitive'])
const cap = args.max_agents || 4
const tasks = (args.tasks || [])
const launched = tasks.slice(0, cap)
const notLaunched = tasks.slice(cap)
if (notLaunched.length) log(`cap ${cap}: ${notLaunched.length} task(s) not launched this wave: ${notLaunched.map(t => t.id).join(', ')}`)
if (!launched.length) return { error: 'no tasks', launched: 0 }

const list = (xs) => (xs && xs.length ? xs.map(x => `- ${x}`).join('\n') : '- (none)')

function workerPrompt(t) {
  const iso = args.isolation === 'worktree'
    ? `Isolation: worktree mode. You are already in a fresh worktree of ${args.repo}. Commit on your branch after every green step; never on the target branch.`
    : `Isolation: copy mode. Create your copy first: rsync -a --exclude .git --exclude <dependency dir> ${args.repo}/ ${args.scratch}/${t.id}/ ; then in the copy: git init -q && git add -A && git commit -qm baseline ; then ${stack.deps_sync || 'install dependencies (deps-sync in STACK.md)'}. Work only there. After every green step write a checkpoint patch: git -C ${args.scratch}/${t.id} diff --binary > ${args.scratch}/${t.id}-checkpoint.patch. At the end write ${t.id}-main.patch (your files) and, only if you had to touch shared hot files, ${t.id}-shared.patch, in ${args.scratch}/.`
  return `You are a worker agent building ${t.id}: ${t.goal}
Execute directly. Do not spawn agents. Return the structured report once at the end, then stop.

## Read first
${list(t.read_first)}

## Scope
In:
${list(t.scope_in)}
Out:
${list(t.scope_out)}

## Files you may write (everything else is read-only)
${list(t.writable)}
Do NOT edit the shared hot files (workstream-tracking, "Shared hot files"). If you need a change there, put the exact snippet in needs_from_coordinator.

## Resources
${iso}
Database: ${t.db || 'a test container or your own throwaway database'}. Off limits: ${args.off_limits || 'the developer database, compose volumes, servers you did not start'}.
Ports for anything you start: ${t.ports || 'none assigned; do not start servers'}.

## Acceptance criteria
${list(t.acceptance)}

## Verify (paste real counts into the report and the change record)
${list(t.verify && t.verify.length ? t.verify : [stack.check || 'check (STACK.md)'])}

## Safety
Stop only processes you started, by PID. If a command is denied, stop and report it; do not work around it. Never print or commit secrets. Do not commit to the target branch, push, or call external services. Never report a result you did not see.

## Report
Fill every field of the structured report. summary is the only prose. workspace is the absolute path of your copy or worktree.`
}

function anchorPrompt(t, report) {
  return `Read-only verification. In the workspace ${report.workspace} (a copy or worktree for task ${t.id}), run exactly: ${stack.check || 'the check command from project-guide/knowledge/STACK.md'} . Do not fix anything, do not edit files. Return the command, its exit code, the passed and failed counts if the output shows them, and the last 15 lines of real output. If the command cannot run, return exit_code -1 and say why in output_tail.`
}

function reviewPrompt(t, report, lensKey) {
  return `Read-only review of task ${t.id} (${t.change_type}) in workspace ${report.workspace}. Lens: ${LENSES[lensKey]}
Read the change record at ${report.change_record || '(path in the report)'} and the diff: git -C ${report.workspace} diff baseline (copy mode) or git diff <target> (worktree mode). Use engineering-standards/references/review-checklist.md items that belong to your lens. Judge the diff, not the record's claims. Acceptance criteria:
${list(t.acceptance)}
Report findings as where / issue / fix, ranked must_fix, should_fix, nits, and whether you would integrate as is.`
}

// one pipeline per task: build → anchor → review. No barrier: task A can be in review while B still builds.
const results = await pipeline(
  launched,
  (t) => agent(workerPrompt(t), { label: `build:${t.id}`, phase: 'Build', schema: WORKER_REPORT, agentType: types.worker, isolation: args.isolation === 'worktree' ? 'worktree' : undefined }),
  async (report, t) => {
    if (!report || !report.workspace) return { report, anchor: null }
    const anchor = await agent(anchorPrompt(t, report), { label: `anchor:${t.id}`, phase: 'Anchor', schema: ANCHOR, agentType: types.anchor, effort: 'low' })
    return { report, anchor }
  },
  async (prev, t) => {
    const { report, anchor } = prev
    if (!report || !report.workspace) return { task: t, report, anchor, reviews: [] }
    const lenses = heavy.has(t.change_type) ? Object.keys(LENSES) : ['correctness']
    const reviews = (await parallel(lenses.map(l => () =>
      agent(reviewPrompt(t, report, l), { label: `review:${t.id}:${l}`, phase: 'Review', schema: VERDICT, agentType: types.reviewer })))).filter(Boolean)
    return { task: t, report, anchor, reviews, lenses }
  },
)

// ---- reduce in plain code: fan-in guard, verdicts, rows for the coordinator ----
const returned = results.filter(Boolean)
const lost = launched.length - returned.length
if (lost > 0) log(`WARNING: ${lost} of ${launched.length} task pipelines returned nothing (killed or errored). Their copies may hold checkpoint patches under ${args.scratch}.`)

const perTask = launched.map((t, i) => {
  const r = results[i]
  if (!r || !r.report) return { id: t.id, outcome: 'lost', title: t.title, hint: `look for ${args.scratch}/${t.id}-checkpoint.patch` }
  const { report, anchor, reviews, lenses } = r
  const anchorGreen = !!anchor && anchor.exit_code === 0
  const mustFix = reviews.flatMap(v => (v.must_fix || []).map(f => Object.assign({ lens: v.lens }, f)))
  const votes = reviews.filter(v => v.integrate_as_is).length
  const majority = reviews.length ? votes * 2 > reviews.length : false
  const claimsGreen = (report.verification || []).every(v => v.exit_code === 0)
  const outcome = report.status !== 'done' ? report.status
    : !anchorGreen ? 'anchor-red'
    : mustFix.length || !majority ? 'needs-fixes'
    : 'verified'
  return {
    id: t.id, title: t.title, change_type: t.change_type, outcome,
    worker_status: report.status, worker_claims_green: claimsGreen, anchor_green: anchorGreen,
    anchor: anchor && { exit_code: anchor.exit_code, passed: anchor.passed, failed: anchor.failed, output_tail: anchor.output_tail },
    reviews: { lenses: lenses || [], integrate_votes: votes, must_fix: mustFix, should_fix: reviews.flatMap(v => v.should_fix || []) },
    workspace: report.workspace, patches: report.patches || {}, change_record: report.change_record,
    files_changed: report.files_changed, summary: report.summary,
    needs_from_coordinator: report.needs_from_coordinator || [], decisions_needed: report.decisions_needed || [], deviations: report.deviations || [],
    ledger_row: report.ledger_row || `| ${t.id} | ${t.title} | | ${report.status} | Claude (subagent) | ${(t.writable || []).join(', ')} | ${report.change_record || ''} |`,
    index_row: report.index_row || '',
  }
})

const count = (k) => perTask.filter(x => x.outcome === k).length
const metrics = {
  tasks_in_wave: tasks.length, launched: launched.length, not_launched: notLaunched.map(t => t.id),
  returned: returned.length, lost, verified: count('verified'), needs_fixes: count('needs-fixes'),
  anchor_red: count('anchor-red'), partial: count('partial'), blocked: count('blocked'),
  worker_claimed_green_but_anchor_red: perTask.filter(x => x.worker_claims_green && x.anchor && !x.anchor_green).length,
  must_fix_findings: perTask.reduce((n, x) => n + ((x.reviews && x.reviews.must_fix.length) || 0), 0),
  agents_used: launched.length + perTask.filter(x => x.anchor).length + perTask.reduce((n, x) => n + ((x.reviews && x.reviews.lenses.length) || 0), 0),
  tokens_spent: budget.spent(),
}
log(`wave: ${metrics.verified} verified, ${metrics.needs_fixes} need fixes, ${metrics.anchor_red} anchor red, ${metrics.partial + metrics.blocked} partial/blocked, ${lost} lost, ${notLaunched.length} not launched`)

return {
  metrics,
  tasks: perTask,
  next_for_coordinator: [
    'Integrate verified tasks per multi-agent-development/references/integration-checklist.md (main patch, then shared patch by hand, then deps-lock if the manifest changed, then the touched checks).',
    'Send needs-fixes and anchor-red tasks back to the same worker with the must_fix list and the anchor output; do not fix them yourself.',
    'Resume lost tasks from their checkpoint patches; do not relaunch on the same files.',
    'Paste metrics into HANDOFF.md "Wave metrics", update ledger rows from ledger_row, INDEX rows from index_row, then run check-all on the integrated branch.',
  ],
}
