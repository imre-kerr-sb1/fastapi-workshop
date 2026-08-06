# Loose tasks

Tasks (or just infodumps) that have not yet been placed in the outline.

Everything that used to be here is placed now — dev/prod differences landed in
section 3 as the hello-world "observe → why", and all three status-code cases became
section 7, with the get-or-create trick turning into the upsert PUT.

## Still unplaced

- **Decide the timeline lever, and do it soon.** The outline is 3:15 of content with no
  slack, and the four options are written up at the top of it. Asking for 3.5 hours is
  the cheapest; pre-baking the setup into the Coder image is the highest-leverage. Both
  need doing before the invite goes out, so this is the one blocking task.
- **The PokeAPI screenshot is no longer needed.** The species/form split was only load-
  bearing for the long design section; Alolan Vulpix is now an optional sixty-second aside
  that doesn't reference PokeAPI at all. The firewall blocks pokeapi.co from Coder
  workspaces, so this is a relief rather than a loss.
- **Do participants push to their repos?** They create one in section 2 and then it's
  never mentioned again. Either drop the repo step or end with "commit and push" — and
  since persistence is cut there's no `workshop.db` to gitignore any more, so this is now
  purely a question of whether they leave with something they can find again.
- **Escape hatch for people who fall behind.** Someone will pick an ambitious domain
  in section 4 and still be modelling it at the break. Worth having a "copy this and
  move on" snippet ready, maybe just the Pokémon model.
- **Does section 5 land as a discussion?** It's the only building-half section with no
  typing, and it's carrying the workshop's one genuinely opinionated claim ("POST creates,
  PUT updates" is a consequence, not a rule). If the room is quiet rather than engaged,
  ten minutes will feel like twenty. Fallback: skip straight to "everyone decides now"
  and let the design speak for itself in sections 6 and 7.
- **Section 1 is untested on a real room.** Thirty minutes of talking with no laptops is
  a lot, and it's the section this audience most needs. Worth rehearsing out loud with a
  timer — if it runs to 40, something has to give elsewhere. The whiteboard
  request/response diagram and the "serve it from a raw socket" list are the two bits
  that earn their time; the rest can compress.

Deferred rather than unplaced: `response_model` vs return annotations, 405 /
trailing-slash behaviour, and PATCH. All parked in [next-time.md](next-time.md)
section 7.
