# Loose tasks

Tasks (or just infodumps) that have not yet been placed in the outline.

Everything that used to be here is placed now — dev/prod differences landed in
section 2 as the hello-world "observe → why", and all three status-code cases became
section 5, with the get-or-create trick turning into create-or-replace on PUT.

## Still unplaced

- **Timing is a guess.** The table in the outline adds up to exactly 3:00, which is
  suspicious. Sections 4 and 5 are the ones most likely to overrun, and 6 is the one
  that can absorb it (it's drop-in-a-file).
- **Do participants push to their repos?** They create one in section 1 and then it's
  never mentioned again. Either drop the repo step or end with "commit and push", and
  if the latter, the `.gitignore` needs `workshop.db` in it.
- **Escape hatch for people who fall behind.** Someone will pick an ambitious domain
  in section 3 and still be modelling it at the break. Worth having a "copy this and
  move on" snippet ready, maybe just the Pokémon model.
- **Untried: response_model vs return annotations.** The outline uses return
  annotations throughout, which is the modern style, but `response_model` is all over
  older docs and Stack Overflow answers. Might be worth 2 minutes so people can read
  older material. Might be a distraction.
- **Nothing covers 405 or trailing-slash behaviour.** Both are common real-world
  confusions and both are basically free to demonstrate, but neither fits a section.
