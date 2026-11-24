# Game Fish ID Quiz

A browser game for learning to identify North American game fish from real
iNaturalist observation photos. Pick a state or province, freshwater, saltwater
or both, and a field-guide section, then name the fish.

Everything is in a single `index.html` file with no build step and no dependencies.

## Features

- **Any US state, Canadian province or territory**, plus all of the US or all of Canada.
- **Freshwater / Saltwater / Both.** Anadromous and brackish species (salmon,
  steelhead, striped bass, shad, sturgeon, tarpon, snook, bull shark) count as both.
- **14 field-guide sections.** Freshwater: trout, salmon & char; black bass &
  sunfish; perch, walleye & sauger; pike, pickerel & muskie; catfish & bullheads;
  temperate bass; gar, bowfin, sturgeon & more. Saltwater: drums & croakers;
  snappers & groupers; jacks & pompano; tunas & mackerels; billfish & inshore
  gamefish; flatfish & bottomfish; sharks.
- **124 curated species**, each with a field-marks ID tip.
- **Live data.** Each game asks iNaturalist which of these species have
  research-grade records in the chosen place, then shows Creative Commons photos
  from that place, credited to the photographers.
- **Question types:** Photo ID, Field marks (identify from the written
  description), or Mixed.
- **Scoring:** streak bonus, hints for half points, a best score saved per set of
  settings, and a "study these" list of missed fish at the end.
- **Field guide tab** with cards for every species recorded in the chosen place,
  linking to iNaturalist, Wikipedia and FishBase.
- **Keyboard:** 1–6 to answer, H for a hint, Enter for the next fish.

## Run it

Open `index.html` in any modern browser. It needs an internet connection to
reach the iNaturalist and Wikipedia APIs.

## Publish on GitHub Pages

1. Create a new repository, e.g. `gamefish-quiz`.
2. Add `index.html` and this `README.md`, then commit.
3. Go to **Settings → Pages → Build and deployment**, choose **Deploy from a
   branch**, then select `main` and `/ (root)`.
4. After a minute or so the game is live at
   `https://<your-username>.github.io/gamefish-quiz/`.

## Editing the species list

Species live in the `RAW` block near the top of the script, one per line:

```
section|habitat|Common name|Scientific name;synonym|Field marks
bass|f|Largemouth Bass|Micropterus nigricans;Micropterus salmoides|Upper jaw extends past the eye...
```

- `habitat`: `f` freshwater, `s` saltwater, `b` both.
- `section`: one of the keys in `SECTIONS`. Add a key there to create a new section.
- Add synonyms after a `;` when iNaturalist uses a different scientific name.
  Largemouth Bass and Bowfin were both recently split, for example. Matching
  falls back to the iNaturalist common name.

## Data and credits

- Photos and occurrence counts come from [iNaturalist](https://www.inaturalist.org)
  community observations. Only research-grade observations with Creative Commons
  or CC0 photo licenses are used, and each photo shows its attribution.
- Summaries come from the [Wikipedia REST API](https://en.wikipedia.org/api/rest_v1/).
- Species pages link to [FishBase](https://www.fishbase.se).
- API requests are spaced about one second apart, in line with iNaturalist's API
  guidance. Results are cached in the browser for seven days.
- "Recorded here" means at least one research-grade iNaturalist observation in
  that place. It is not an official range map. Check your state's fishing
  regulations before keeping fish.

## License

Code: MIT (see LICENSE). Photos remain under their photographers' Creative Commons licenses.
