# copilot_session.md

## Project
phc — PHC Lab Compliance Tracker

## Objective
Build a fresh single-purpose Django monolith for one fixed PHC/MSDS Clinical/Pathology Laboratory checklist.

## Scope boundary
Do not rebuild old AccrediOps complexity. No multi-framework builder, no CAPA board, no Next.js split, no live-AI dependency in MVP.

## Deployment target
- Repository/folder name: `phc`
- Server path: `/home/munaim/srv/apps/phc`
- Public domain: `https://phc.alshifalab.pk`
- App internal Docker port mapping: `127.0.0.1:8018 -> web:8000`
- Caddy reverse proxy should route `phc.alshifalab.pk` to `127.0.0.1:8018`

## Session plan
- [ ] Review source materials in `data/source_materials/`
- [ ] Create Django project and apps
- [ ] Implement locked 118-indicator model and seed/import command
- [ ] Implement compliance/evidence tracking
- [ ] Implement evidence library with evidence categories
- [ ] Implement digital register definitions and entries
- [ ] Implement recurring due/overdue logic
- [ ] Implement dashboard
- [ ] Implement printable reports
- [ ] Add tests
- [ ] Add Caddy deployment block/instructions
- [ ] Update documentation
- [ ] Commit changes

## Completed work
None yet.

## Pending work
All implementation pending.

## Handoff notes
Keep this file updated throughout development.
