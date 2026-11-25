# Game Fish ID Quiz

A browser game for learning to identify North American game fish from real
iNaturalist observation photos. Pick a state or province, freshwater, saltwater
or both, and a field-guide section, then name the fish.

The game is a static page (`index.html` + `data/species.js`). A GitHub Action rebuilds the species list from FishBase once a month.

## Features

- **Any US state, Canadian province or territory**, plus all of the US or all of Canada.
- **Freshwater / Saltwater / Both.** Anadromous and brackish species (salmon,
  steelhead, striped bass, shad, sturgeon, tarpon, snook, bull shark) count as both.
- **14 field-guide sections.** Freshwater: trout, salmon & char; black bass &
  sunfish; perch, walleye & sauger; pike, pickerel & muskie; catfish & bullheads;
  temperate bass; gar, bowfin, sturgeon & more. Saltwater: drums & croakers;
  snappers & groupers; jacks & pompano; tunas & mackerels; billfish & inshore
  gamefish; flatfish & bottomfish; sharks.
- **About 580 species**: every fish FishBase flags as a game fish in the US or
  Canada, plus 124 hand-curated species with angler-friendly ID tips. Other
  species get clues from FishBase's diagnosis text, family and size.
- **Where:** a fish counts for a state or province if it's on FishBase's checklist
  for that place *or* has iNaturalist observations there. Choose **Anywhere in
  North America** to ignore location, or **Core list** to stick to the curated species.
- **Photos never exclude a fish.** The game uses research-grade photos from the
  chosen place first, then research-grade photos from anywhere, then
  unconfirmed observations, then the species' iNaturalist taxon photos. Each
  photo shows its credit and whether it was taken locally.
- **Question types:** Photo ID, Field marks (identify from the written
  description), or Mixed.
- **Scoring:** streak bonus, hints for half points, a best score saved per set of
  settings, and a "study these" list of missed fish at the end.
- **Field guide tab** with cards for every species recorded in the chosen place,
  linking to iNaturalist, Wikipedia and FishBase.
- **Keyboard:** 1–6 to answer, H for a hint, Enter for the next fish.

## Run it

Open `index.html` in any modern browser, keeping the `data` folder next to it.
It needs an internet connection to reach the iNaturalist and Wikipedia APIs.

## Publish on GitHub Pages

1. Create a new repository, e.g. `gamefish-quiz`.
2. Add `index.html` and this `README.md`, then commit.
3. Go to **Settings → Pages → Build and deployment**, choose **Deploy from a
   branch**, then select `main` and `/ (root)`.
4. After a minute or so the game is live at
   `https://<your-username>.github.io/gamefish-quiz/`.

## How the species list is built

`scripts/build_species.py`, run by `.github/workflows/build-species.yml`:

1. Downloads the open FishBase tables (`species`, `country`, `countrysub`, `families`,
   `morphdat`) from the [FishBase data release on Hugging Face](https://huggingface.co/datasets/cboettig/fishbase).
2. Keeps species that are native or introduced in the US or Canada and flagged as
   game fish (FishBase's country-level `Game` or species-level `GameFish`).
3. Adds the state/province checklist, habitat flags, family, maximum length and
   diagnosis text, and assigns a field-guide section by family.
4. Looks up each species' iNaturalist taxon id, common name and photo (cached
   between builds).
5. Writes `data/species.js` and a summary in `data/build_report.txt`.

The Action runs on the 3rd of each month, whenever the script or curated list
changes, or on demand from **Actions → Build species list → Run workflow**.

## Editing the curated species

Hand-curated species live in `scripts/curated.tsv`, one per line. Their names,
sections and tips override FishBase's. Committing a change rebuilds the data automatically.

```
section|habitat|Common name|Scientific name;synonym|Field marks
bass|f|Largemouth Bass|Micropterus nigricans;Micropterus salmoides|Upper jaw extends past the eye...
```

- `habitat`: `f` freshwater, `s` saltwater, `b` both.
- `section`: one of the keys in `SECTIONS` (in `index.html`) and `FAM_SECTION` (in the build script).
- Add synonyms after a `;` when iNaturalist uses a different scientific name.
  Largemouth Bass and Bowfin were both recently split, for example. Matching
  falls back to the iNaturalist common name.

## Data and credits

- Species list, state checklists and diagnoses: [FishBase](https://www.fishbase.se)
  (Froese & Pauly, eds.), CC BY-NC.
- Photos and occurrence counts come from [iNaturalist](https://www.inaturalist.org)
  community observations. Only Creative Commons or CC0 licensed photos are used,
  and each photo shows its attribution.
- Summaries come from the [Wikipedia REST API](https://en.wikipedia.org/api/rest_v1/).
- Species pages link to [FishBase](https://www.fishbase.se).
- API requests are spaced about one second apart, in line with iNaturalist's API
  guidance. Results are cached in the browser for seven days.
- Neither FishBase's state checklists nor iNaturalist records are complete range
  maps. Check your state's fishing
  regulations before keeping fish.

## License

Code: MIT (see LICENSE). Photos remain under their photographers' Creative Commons licenses.
