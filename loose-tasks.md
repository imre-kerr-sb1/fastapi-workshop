# Loose tasks

Tasks (or just infodumps) that have not yet been placed in the outline.

Everything that used to be here is placed now — dev/prod differences landed in
section 2 as the hello-world "observe → why", and all three status-code cases became
section 6, with the get-or-create trick turning into the upsert PUT.

## Still unplaced

- **Timing has 15 minutes of real slack now**, for the first time. Cutting the long API
  design section down to a 10-minute discussion (section 4) freed it. Spend it on the
  optional POST / auto-ID / `Location` demo if the day runs clean, otherwise let it absorb
  overrun. Compress 7 first if you're still behind.
- **The PokeAPI screenshot is no longer needed.** The species/form split was only load-
  bearing for the long design section; Alolan Vulpix is now an optional sixty-second aside
  that doesn't reference PokeAPI at all. The firewall blocks pokeapi.co from Coder
  workspaces, so this is a relief rather than a loss.
- **Do participants push to their repos?** They create one in section 1 and then it's
  never mentioned again. Either drop the repo step or end with "commit and push", and
  if the latter, the `.gitignore` needs `workshop.db` in it.
- **Escape hatch for people who fall behind.** Someone will pick an ambitious domain
  in section 3 and still be modelling it at the break. Worth having a "copy this and
  move on" snippet ready, maybe just the Pokémon model.
- **Does section 4 land as a discussion?** It's the only section with no typing, and it's
  carrying the workshop's one genuinely opinionated claim ("POST creates, PUT updates" is
  a consequence, not a rule). If the room is quiet rather than engaged, ten minutes will
  feel like twenty. Fallback: skip straight to "everyone decides now" and let the design
  speak for itself in sections 5 and 6.

Deferred rather than unplaced: `response_model` vs return annotations, 405 /
trailing-slash behaviour, and PATCH. All parked in [next-time.md](next-time.md)
section 6.
