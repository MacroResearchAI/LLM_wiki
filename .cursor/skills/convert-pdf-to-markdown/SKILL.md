---
name: convert-pdf-to-markdown
description: Convert PDF papers to markdown with marker using a robust Windows workflow. Use when the user asks to convert a PDF to markdown or MD, says things like "convert this pdf to md file", "convert this paper to markdown", "turn this pdf into markdown", "extract the main body from this pdf", or needs main-body-only extraction, appendix exclusion, chunked marker conversion, stale artifact cleanup, temporary chunk cleanup, or post-conversion repair of equation tags and broken inline math.
---

# Convert PDF to Markdown

## Goal

Convert a PDF into a markdown file using `marker` with a workflow that is reliable on Windows for long academic papers.

Default behavior:
- convert the main body only
- exclude the appendix
- use chunked conversion
- write the final markdown beside the PDF
- write temporary chunk outputs under `scripts/temporary/`
- remove stale incomplete artifacts before reruns
- after assembly, repair detached equation tags and broken inline math

## When to Use

Use this skill when:
- the user asks to convert a PDF to markdown
- the user asks to convert a PDF to MD
- the user says `convert this pdf to md file`
- the user says `convert this paper to markdown`
- the user says `turn this pdf into markdown`
- the user says `extract this pdf into markdown`
- the user says `extract the main body from this pdf`
- `marker_single.exe` hangs or long single-pass conversion stalls
- the user wants main-body-only conversion without appendix
- a prior conversion left partial output folders or temporary chunks

## Trigger Examples

Typical requests that should trigger this skill:

- `convert this pdf to md file`
- `convert this paper to markdown`
- `turn this pdf into markdown`
- `extract this pdf into md`
- `convert this academic paper to markdown`
- `convert only the main body of this pdf`
- `exclude the appendix and convert this pdf to markdown`

## Rules

- Before any command or edit, report the issue, give a short plan, and wait for `proceed`.
- Prefer the direct Python entrypoint over the Windows `.exe` wrapper:
  - `python -c "from marker.scripts.convert_single import convert_single_cli; convert_single_cli()"`
- Prefer `--disable_multiprocessing` on Windows.
- Prefer `--disable_ocr` for text-based academic PDFs unless the PDF is clearly scanned.
- Put temporary chunk outputs under `scripts/temporary/<run-name>/`.
- If the user asks for main body only, detect the appendix boundary first and convert only pages before it.
- Remove stale incomplete artifact folders before a fresh rerun.
- Do not delete the final assembled markdown unless the user asks.

## Workflow

1. Verify prerequisites
   - Confirm Python `>=3.10`.
   - Confirm `marker-pdf` is installed in that interpreter.
   - If `marker_single.exe` is not on `PATH`, do not rely on it.

2. Detect appendix boundary
   - Use `pypdfium2` text extraction to scan pages for terms like:
     - `appendix`
     - `online appendix`
     - `technical appendix`
     - `data appendix`
   - Verify the likely boundary by checking nearby pages.
   - Use zero-based page ranges for `marker`.

3. Clean stale artifacts
   - If an old output folder exists beside the PDF and is known to be partial, remove it before rerunning.
   - If rerunning a chunked workflow, use a fresh temp directory under `scripts/temporary/`.

4. Probe with a small chunk
   - Run pages `0-4` first.
   - Confirm that markdown is actually written.
   - Only continue once the probe succeeds.

5. Convert in chunks
   - For long PDFs, use chunks of about 5 pages.
   - Run chunks sequentially.
   - Verify each chunk markdown file exists before proceeding.

6. Assemble the final markdown
   - Concatenate chunk markdown files in page order.
   - Write the final file beside the PDF.
   - Use a suffix like ` - main body.md` when excluding appendix.

7. Repair equation tags and inline math
   - Run the repairs in [Math cleanup](#math-cleanup) on the assembled markdown before reporting.
   - Do not leave this step for a later request. It is part of the conversion.

8. Report caveats
   - `marker` output may include encoding artifacts such as `â€”` or dropped ligatures.
   - Offer mojibake cleanup only if the user wants it.
   - Equation-tag and inline-math repairs are already applied in step 7.

9. Cleanup
   - If the user asks, delete the temporary chunk workspace after verifying the final file exists.

## Commands

Use this Python entrypoint:

```powershell
& "$PYTHON311" -c "from marker.scripts.convert_single import convert_single_cli; convert_single_cli()"
```

Recommended conversion flags for long text PDFs:

```powershell
--disable_tqdm --disable_multiprocessing --disable_ocr --output_format markdown
```

Example single chunk:

```powershell
& "$PYTHON311" -c "from marker.scripts.convert_single import convert_single_cli; convert_single_cli()" `
  --disable_tqdm `
  --disable_multiprocessing `
  --disable_ocr `
  --page_range 0-4 `
  --output_format markdown `
  --output_dir "d:\IdeasIncubator\scripts\temporary\marker_run\probe" `
  "d:\IdeasIncubator\FXI\reference\paper.pdf"
```

## Appendix Detection

Use a quick text scan with `pypdfium2`:

```powershell
& "$PYTHON311" -c "import pypdfium2 as pdf; path=r'd:\IdeasIncubator\FXI\reference\paper.pdf'; doc=pdf.PdfDocument(path); hits=[]; 
for i in range(len(doc)):
    txt=doc[i].get_textpage().get_text_range().replace('\r',' ').replace('\n',' ')
    low=txt.lower()
    if 'appendix' in low or 'online appendix' in low or 'technical appendix' in low or 'data appendix' in low:
        snippet=txt[:220].encode('ascii','ignore').decode('ascii')
        hits.append((i, snippet))
print(hits[:20])"
```

Then inspect nearby pages to confirm the true start.

## Chunking Pattern

Use this pattern for main-body chunk ranges:

- 5-page chunks by default
- final chunk can be shorter
- examples:
  - `0-4`, `5-9`, `10-14`
  - final short chunk like `45-48`

For each chunk:
- create a dedicated temp output directory
- run the conversion
- verify `<pdf-basename>.md` exists in the expected nested output folder

## Assembly Pattern

Assemble in page order:

1. probe chunk
2. remaining chunks in ascending range order

Write to:
- `<pdf name> - main body.md` when excluding appendix
- otherwise `<pdf name>.md` if the user wants the whole document

## Output Paths

Expected marker chunk output structure:

```text
<chunk-output-dir>/<pdf-basename>/<pdf-basename>.md
```

Final output should be written beside the source PDF.

Temporary outputs should live under:

```text
scripts/temporary/<run-name>/
```

## Math cleanup

Apply this to the assembled markdown. Display equations that already end with `\tag{N}` inside `$$...$$` stay as they are. Recover ambiguous symbols from the PDF text (`pypdfium2`), not from the broken markdown alone, and say which reconstructions came from the PDF.

### Equation tags

Marker often drops the equation number onto the next line, or writes it as its own display.

Target form, inside the display math:

```markdown
$$... , \tag{18}$$
```

or, when the equation already ends with a period:

```markdown
$$... . \tag{7}$$
```

Repair these cases:

- A display equation followed by a line that is only `(N)` or ` (N)`: delete that line and append `, \tag{N}` or `. \tag{N}` to the equation, keeping the punctuation already there. Do not add a second comma or period.
- A line that is only `$$(N)$$`: delete it and put `\tag{N}` on the preceding display equation.
- A number left inside the math as `. (N)$$`: change it to `. \tag{N}$$`.
- An existing tag jammed against the punctuation, `,\tag{N}` or `.\tag{N}`: insert the space, `, \tag{N}` or `. \tag{N}`.
- If one number follows two split displays, attach `\tag{N}` to the line that carries that number in the PDF. Leave the unnumbered continuation untagged.

### Inline math

Rewrite prose symbols as `$...$`. Do not alter display equations except for the tag repairs above.

Common Marker failures and the repair:

- `<sup>...</sup>` used as a subscript or superscript: `g<sup>i</sup>` → `$g_i$`, `λ<sup>S</sup>` → `$\lambda_S$`, `µ<sup>t</sup>` → `$\mu_t$`, `φ<sup>m</sup>` → `$\phi_m$`.
- A trailing `b` that is a hat, not the letter b: `<sup>Π</sup>b` and `<sup>ρ</sup><sup>b</sup>` → `$\widehat{\Pi}$` and `$\hat{\rho}$`. Confirm with the PDF before moving the hat, because Marker often attaches `b` to the wrong symbol. Example: markdown `ρ > ρ<sup>b</sup>` is `$\hat{\rho} > \rho$` when the PDF has `\hat{\rho} > \rho`.
- `6=` or `<sup>6</sup><sup>=</sup>` is `\neq`, not the digit 6. Example: `<sup>ρ</sup>b<sup>+</sup> <sup>6</sup><sup>=</sup> <sup>ρ</sup>b<sup>−</sup>` → `$\hat{\rho}^{+} \neq \hat{\rho}^{-}$`.
- A trailing `0` on an index is a prime: `Πss<sup>0</sup>` → `$\Pi_{ss'}$`.
- Run-together indices and bars: `sij` → `$s_{ij}$`, `eij,t` → `$e_{ij,t}$`, `Pi,d,t` → `$\mathcal{P}_{i,d,t}$`, `ZS,t` → `$Z_{S,t}$`, `YS,t` → `$Y_{S,t}$`, `K¯ j` → `$\bar{K}_j$`, `¯d` → `$\bar{d}$`, `V C,m d,t` → `$V^{C,m}_{d,t}$`.
- A tilde dumped as a leading letter: `<sup>z</sup>e<sup>t</sup> = log <sup>Z</sup>S,t <sup>−</sup> <sup>z</sup>¯S` → `$\widetilde{z}_t = \log Z_{S,t} - \bar{z}_S$`.
- Split switching-cost indices: `χ<sup>r</sup>−<sup>j</sup>` → `$\chi_{r_{-}j}$`, `χ<sup>∅</sup><sup>j</sup>` → `$\chi_{\varnothing j}$`.

After the repair, the assembled file should contain no `<sup>` tags and no equation number sitting outside its display.

## Report Format

Report only:
- appendix start page used
- page range converted
- final output path
- whether temp chunks were kept or deleted
- whether there are visible encoding artifacts
- which equation tags were folded in
- which inline-math reconstructions were taken from the PDF because the markdown order was ambiguous

## Failure Handling

- If the probe chunk fails, stop and report the exact failing command.
- If a chunk batch is interrupted, inspect which chunk markdown files already exist and resume only missing chunks.
- If a single-pass conversion hangs with no file updates, switch to chunked conversion.
- If the Windows wrapper hangs, use the direct Python entrypoint instead of `marker_single.exe`.
