# AssetLens — JKUAT Asset Valuation Dashboard

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Place `asset_snippet_visualize.xlsx` in the same directory as `app.py`.
If the file is not present, the app will prompt for an upload on first load.

---

## Migration Checklist

1. **Streamlit version** — Verify `streamlit >= 1.33.0` is installed (`streamlit version`). Required for `@st.fragment` support.

2. **Create directory structure** — Run:
   ```bash
   mkdir -p pages components charts
   ```

3. **Delete removed files** — Remove `valuation_engine.py` from the project root. It is no longer used.

4. **Initialise session_data.json** — An empty `session_data.json` is included. Do not delete it — the app reads it on every load. If it gets corrupted, replace with:
   ```json
   {"tag_updates":{},"missing_flags":[],"new_assets":[],"pending_values":{},"condition_edits":{},"row_edits":{}}
   ```

5. **Excel file location** — Place `asset_snippet_visualize.xlsx` in the project root (same folder as `app.py`). The `DATA_FILE` constant in `app.py` controls this path.

6. **Clear Streamlit cache** — After deploying, clear browser cache and run `streamlit cache clear` to avoid stale `@st.cache_data` hits from the old app.

7. **Browser cache** — Hard-refresh the browser (`Ctrl+Shift+R` / `Cmd+Shift+R`) after first deploy to pick up new CSS in `styles.py`.

8. **Sidebar state** — The sidebar is set to `collapsed` by default in `st.set_page_config`. Navigation is handled via sidebar buttons styled as a topbar. Do not change `initial_sidebar_state`.

9. **session_data.json permissions** — Ensure the process running Streamlit has write access to the project directory. The sidecar uses atomic writes (`os.replace`) — the directory must be writable.

10. **Pending valuation persistence** — Values entered in the Pending Valuation tab are written to `session_data.json` immediately. Back up this file before redeploying or overwriting the Excel source.

11. **New asset buildings dropdown** — The "Add asset" form populates the Building dropdown from live data filtered by selected campus. If a campus has no buildings in the register, it will show "UNASSIGNED". This resolves itself once real building data is loaded.

12. **Large export performance** — The Excel export generates 5 sheets from 63,000+ rows. On first click, allow 5–10 seconds for generation. Subsequent clicks use the same session data and are faster.
