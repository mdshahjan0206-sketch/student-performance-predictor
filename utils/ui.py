"""
Presentation-layer helpers for the premium UI design system.

IMPORTANT: This module is purely cosmetic. It does not read or write any
application/session state related to datasets, models, or predictions.
It only renders markup and injects CSS so every page shares one consistent,
premium look and feel.
"""

import os
import re
import html
import textwrap
import functools
import streamlit as st

_CSS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "css", "style.css")
_DESIGN_SYSTEM_CSS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "css", "design-system.css")
_PREMIUM_BUTTON_CSS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "css", "premium-button.css")


@functools.lru_cache(maxsize=None)
def _read_text_file(path: str) -> str:
    """Read a static asset file once per process and keep it in memory.

    PERFORMANCE: inject_global_css() runs at the top of every single page,
    on every rerun (every widget interaction). Without this cache, that
    meant re-opening and re-reading ~150KB of CSS from disk on every rerun
    of every page — pure I/O with no benefit, since these files never
    change while the app is running. functools.lru_cache is a plain
    process-level cache (not Streamlit's per-session st.cache_data), which
    is exactly right here: static file content is identical for every
    user/session, so there's no reason to key it per-session at all.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _clean(html: str) -> str:
    """
    Normalize indentation on multi-line HTML/script strings.

    ROOT CAUSE FIX: when a triple-quoted HTML string keeps the same
    indentation as the surrounding Python code (commonly 8-12 spaces), the
    first line is indented 4+ spaces, so Streamlit's Markdown parser
    classifies the whole block as an *indented code block* instead of raw
    HTML — the tags then print literally on screen instead of rendering.
    Dedenting to column 0 before handing the string to st.markdown() is
    what makes it parse as an HTML block. Purely a string-formatting fix;
    it changes no visual output, CSS classes, or content.
    """
    return textwrap.dedent(html).strip()


def inject_global_css():
    """Load the shared stylesheet + sidebar branding. Safe to call on every page.

    File I/O is cached (see _read_text_file) so the CSS is only read from
    disk once per server process; st.markdown() below still runs on every
    rerun (required for Streamlit to keep the <style> tag in the DOM), but
    that's cheap string injection, not a filesystem read.
    """
    try:
        st.markdown(f"<style>{_read_text_file(_CSS_PATH)}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

    try:
        st.markdown(f"<style>{_read_text_file(_DESIGN_SYSTEM_CSS_PATH)}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

    try:
        st.markdown(f"<style>{_read_text_file(_PREMIUM_BUTTON_CSS_PATH)}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

    _inject_premium_button_interactions()

    # Sidebar brand header (purely visual, no state mutation)
    st.sidebar.markdown(
        _clean(
            """
            <div class="pp-sidebar-brand">
                <div class="pp-logo">🎓</div>
                <div>
                    <div class="pp-brand-name">EduPredict AI</div>
                    <div class="pp-brand-tag">Student Performance Platform</div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    _inject_dock_interactions()


def _inject_dock_interactions():
    """
    Pure front-end micro-interaction layer for the sidebar:
      A soft cursor-tracking glow (spotlight) behind the glass sidebar panel.

    Nav-item hover/active/lift states are handled entirely by CSS (see the
    SIDEBAR section in assets/css/style.css) for a clean, minimal feel — this
    script only sets two CSS custom properties based on mouse position.

    Only reads mouse position and toggles CSS custom properties on an
    existing DOM node. Never reads or writes Streamlit session state and has
    zero effect on app behavior or navigation. Guarded with window/element
    flags so re-injection on every Streamlit rerun doesn't stack listeners.
    """
    st.markdown(
        _clean(
            """
            <script>
            (function() {
                if (window.__ppDockBound) { return; }
                window.__ppDockBound = true;

                function setup() {
                    const doc = window.parent ? window.parent.document : document;
                    const sidebar = doc.querySelector('section[data-testid=\\"stSidebar\\"] > div:first-child');
                    if (sidebar && !sidebar.__ppGlowBound) {
                        sidebar.__ppGlowBound = true;
                        sidebar.addEventListener('mousemove', function(e) {
                            const rect = sidebar.getBoundingClientRect();
                            const x = ((e.clientX - rect.left) / rect.width) * 100;
                            const y = ((e.clientY - rect.top) / rect.height) * 100;
                            sidebar.style.setProperty('--pp-mx', x + '%');
                            sidebar.style.setProperty('--pp-my', y + '%');
                        });
                    }
                }

                setup();
                const observer = new MutationObserver(setup);
                const target = (window.parent ? window.parent.document : document).body;
                if (target) {
                    observer.observe(target, { childList: true, subtree: true });
                }
            })();
            </script>
            """
        ),
        unsafe_allow_html=True,
    )


def _inject_premium_button_interactions():
    """
    Pure front-end micro-interaction layer for the premium primary-button
    component (see assets/css/premium-button.css):
      Tracks the cursor over every button[kind="primary"] and writes its
      position into two CSS custom properties, --pb-mx / --pb-my, which
      the stylesheet uses to position the cursor-tracked spotlight and
      the "liquid light reflection" on hover.

    Only reads mouse position and toggles CSS custom properties on
    existing DOM nodes — never reads or writes Streamlit session state,
    never touches widget values, and has zero effect on app behavior,
    click handling, or navigation.

    Streamlit replaces the DOM on every rerun, so buttons are (re)bound
    through a MutationObserver, exactly like _inject_dock_interactions()
    above. A per-element `__ppBtnBound` flag stops duplicate listeners
    from stacking across reruns, and requestAnimationFrame throttles the
    mousemove handler so position updates stay smooth (no layout thrash,
    no lag) regardless of how often the browser fires the event.
    """
    st.markdown(
        _clean(
            """
            <script>
            (function() {
                if (window.__ppBtnBound) { return; }
                window.__ppBtnBound = true;

                const SELECTOR = 'button[kind="primary"], button[data-testid="baseButton-primary"]';
                let ticking = false;
                let pendingBtn = null, pendingX = 50, pendingY = 35;

                function flush() {
                    ticking = false;
                    if (!pendingBtn) return;
                    pendingBtn.style.setProperty('--pb-mx', pendingX + '%');
                    pendingBtn.style.setProperty('--pb-my', pendingY + '%');
                }

                function onMove(e) {
                    const btn = e.currentTarget;
                    const rect = btn.getBoundingClientRect();
                    if (!rect.width || !rect.height) return;
                    pendingBtn = btn;
                    pendingX = ((e.clientX - rect.left) / rect.width) * 100;
                    pendingY = ((e.clientY - rect.top) / rect.height) * 100;
                    if (!ticking) {
                        ticking = true;
                        (window.parent || window).requestAnimationFrame(flush);
                    }
                }

                function onLeave(e) {
                    const btn = e.currentTarget;
                    btn.style.setProperty('--pb-mx', '50%');
                    btn.style.setProperty('--pb-my', '35%');
                }

                function bindAll() {
                    const doc = window.parent ? window.parent.document : document;
                    doc.querySelectorAll(SELECTOR).forEach(function(btn) {
                        if (btn.__ppBtnBound) return;
                        btn.__ppBtnBound = true;
                        btn.addEventListener('mousemove', onMove);
                        btn.addEventListener('mouseleave', onLeave);
                    });
                }

                bindAll();
                const observer = new MutationObserver(bindAll);
                const target = (window.parent ? window.parent.document : document).body;
                if (target) {
                    observer.observe(target, { childList: true, subtree: true });
                }
            })();
            </script>
            """
        ),
        unsafe_allow_html=True,
    )


def sidebar_footer(version: str = "v1.0.0"):
    st.sidebar.markdown(
        _clean(
            f"""
            <div class="pp-sidebar-footer">
                Built with Streamlit &amp; scikit-learn<br/>
                <span style="opacity:.7;">{version}</span>
            </div>
            <div class="pp-sidebar-credit">
                <div class="pp-credit-kicker">👨‍💻 Developed by</div>
                <div class="pp-credit-name">Mohamed Shahjan</div>
                <div class="pp-credit-role">B.E. Computer Science Engineering · Second Year</div>
                <div class="pp-credit-tags">AI · Machine Learning · Python · Data Science</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def custom_radio(*args, **kwargs):
    """
    Drop-in replacement for st.radio() with a premium animated card design.

    IMPORTANT — this is a *thin pass-through wrapper*, not a reimplementation:
    it forwards every positional/keyword argument straight to st.radio() and
    returns its result unchanged. That means selected values, session_state
    behavior, on_change callbacks, form compatibility (works inside
    st.form), and Streamlit's rerun cycle are 100% identical to the native
    widget — nothing about the underlying behavior changes.

    The only difference is visual: the shared stylesheet (see
    "CUSTOM RADIO" section in assets/css/style.css) re-skins every
    st.radio() in the app as a row of bordered, animated selection cards
    with a filling dot indicator instead of the default browser radio
    dots — inspired by the Uiverse-style radio reference. Because the
    styling is applied globally via CSS, calling this function is
    equivalent to calling st.radio() directly; it exists purely so every
    call site in the project shares one obvious, documented, reusable name.

    Use it exactly like st.radio(), e.g.:
        choice = custom_radio("Chart Type", ["Histogram", "Box Plot"], key="dist_chart")
    """
    return st.radio(*args, **kwargs)


def hero(title: str, subtitle: str = "", badge: str = "", icon: str = ""):
    """Animated gradient hero header used at the top of every page."""
    badge_html = f'<div class="pp-hero-badge">{badge}</div>' if badge else ""
    icon_html = f"{icon} " if icon else ""
    st.markdown(
        _clean(
            f"""
            <div class="pp-hero">
                {badge_html}
                <h1>{icon_html}{title}</h1>
                <p>{subtitle}</p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def section_title(title: str, icon: str = "✨", subtitle: str = ""):
    sub_html = f'<span class="pp-sub">{subtitle}</span>' if subtitle else ""
    st.markdown(
        _clean(
            f"""
            <div class="pp-section-title">
                <div class="pp-icon">{icon}</div>
                <div><h3>{title}</h3>{sub_html}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _table_slug(key: str) -> str:
    """Sanitize a key into a safe HTML id fragment."""
    return re.sub(r"[^a-zA-Z0-9_-]", "-", str(key)).strip("-") or "table"


def _format_cell(value) -> str:
    """Render a single cell value as display text. Purely cosmetic formatting —
    does not alter the underlying value the caller passed in."""
    if value is None:
        return "—"
    try:
        import pandas as pd  # local import: this module has no hard pandas dependency otherwise
        if pd.isna(value):
            return "—"
    except Exception:
        pass
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, float):
        # Trim to a readable precision without turning whole numbers into "3.0000"
        return f"{value:.4g}"
    return str(value)


def premium_table(
    df,
    key: str,
    max_rows: int = 300,
    height: int = 420,
    show_download: bool = True,
    download_filename: str = None,
    index_label: str = "",
):
    """
    Render a pandas DataFrame as a premium, on-brand HTML table:
    white surface, rounded corners, soft shadow, thin borders, a soft green
    gradient header, zebra striping, row hover highlight, a sticky header,
    click-to-sort columns, and a responsive/scrollable container.

    Why not st.dataframe(): Streamlit's interactive dataframe widget renders
    its grid on an HTML5 <canvas> (glide-data-grid) inside a sandboxed
    iframe. That canvas can't be restyled with CSS — only its outer wrapper
    (border/shadow/radius) is reachable, which is why the header/zebra/hover
    colors couldn't be made to match the app theme. This component swaps in
    a real HTML table instead, so every requested visual detail is directly
    stylable, while still offering column sorting, scrolling, a sticky
    header, and CSV download.

    IMPORTANT: this function only reads the DataFrame it is given to build
    display markup. It never mutates the DataFrame, never reads or writes
    st.session_state, and performs no data processing, filtering, or ML
    logic — callers pass in the exact same data they previously handed to
    st.dataframe().

    Args:
        df: pandas DataFrame to display.
        key: unique string identifying this table on the page (used to scope
            HTML ids/JS and as the default download filename).
        max_rows: safety cap on rows rendered directly into the DOM, to keep
            large tables fast. The full, uncapped DataFrame is still what
            gets exported by the optional download button.
        height: max pixel height of the scrollable table body before it
            scrolls (sticky header stays visible while scrolling).
        show_download: whether to render a "Download CSV" button above the
            table. Set False on pages that already show their own download
            button for the same data, to avoid a duplicate.
        download_filename: filename for the optional CSV download.
        index_label: header text for the DataFrame's index column. Leave
            blank to use the index's own name, if any.
    """
    if df is None or len(df.columns) == 0:
        return

    import pandas as pd

    total_rows = len(df)
    display_df = df.head(max_rows) if total_rows > max_rows else df
    truncated = total_rows > max_rows

    idx_header = index_label or (df.index.name or "")
    idx_numeric = pd.api.types.is_numeric_dtype(df.index)
    columns = [idx_header] + [str(c) for c in df.columns]
    numeric_flags = [idx_numeric] + [pd.api.types.is_numeric_dtype(df[c]) for c in df.columns]

    header_cells = "".join(
        f'<th data-col="{i}" data-type="{"num" if numeric_flags[i] else "str"}">'
        f'<span class="pp-th-label">{html.escape(col) if col else "&nbsp;"}</span>'
        f'<span class="pp-th-sort">↕</span></th>'
        for i, col in enumerate(columns)
    )

    body_rows = []
    for idx, row in display_df.iterrows():
        values = [idx] + [row[c] for c in df.columns]
        tds = "".join(f"<td>{html.escape(_format_cell(v))}</td>" for v in values)
        body_rows.append(f"<tr>{tds}</tr>")

    table_id = f"pp-table-{_table_slug(key)}"

    if show_download:
        csv_bytes = df.to_csv(index=bool(idx_header)).encode("utf-8")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_bytes,
            file_name=download_filename or f"{_table_slug(key)}.csv",
            mime="text/csv",
            key=f"{table_id}-download",
        )

    if truncated:
        st.markdown(
            f'<div class="pp-table-note">Showing first {max_rows:,} of {total_rows:,} rows — '
            f'use the download button above for the complete data.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        _clean(
            f"""
            <div class="pp-table-wrap" style="max-height:{height}px;">
                <table class="pp-table" id="{table_id}">
                    <thead><tr>{header_cells}</tr></thead>
                    <tbody>{''.join(body_rows)}</tbody>
                </table>
            </div>
            <script>
            (function() {{
                const doc = window.parent ? window.parent.document : document;
                const table = doc.getElementById("{table_id}");
                if (!table || table.__ppSortBound) return;
                table.__ppSortBound = true;

                const getBody = () => table.querySelector("tbody");
                let sortCol = null, sortDir = 1;

                table.querySelectorAll("thead th").forEach(function(th) {{
                    th.addEventListener("click", function() {{
                        const col = parseInt(th.getAttribute("data-col"), 10);
                        const isNum = th.getAttribute("data-type") === "num";
                        sortDir = (sortCol === col) ? -sortDir : 1;
                        sortCol = col;

                        const body = getBody();
                        const rows = Array.from(body.querySelectorAll("tr"));
                        rows.sort(function(a, b) {{
                            const av = a.children[col].textContent.trim();
                            const bv = b.children[col].textContent.trim();
                            if (isNum) {{
                                const an = parseFloat(av.replace(/,/g, "")); 
                                const bn = parseFloat(bv.replace(/,/g, ""));
                                const aNaN = isNaN(an), bNaN = isNaN(bn);
                                if (aNaN && bNaN) return 0;
                                if (aNaN) return 1;
                                if (bNaN) return -1;
                                return (an - bn) * sortDir;
                            }}
                            return av.localeCompare(bv) * sortDir;
                        }});
                        rows.forEach(function(r) {{ body.appendChild(r); }});

                        table.querySelectorAll("thead th").forEach(function(h) {{
                            h.classList.remove("pp-th-active");
                            const arrow = h.querySelector(".pp-th-sort");
                            if (arrow) arrow.textContent = "↕";
                        }});
                        th.classList.add("pp-th-active");
                        const arrow = th.querySelector(".pp-th-sort");
                        if (arrow) arrow.textContent = sortDir === 1 ? "▲" : "▼";
                    }});
                }});
            }})();
            </script>
            """
        ),
        unsafe_allow_html=True,
    )


def badge(text: str, kind: str = "primary"):
    kind_class = "" if kind == "primary" else kind
    st.markdown(f'<span class="pp-badge {kind_class}">{text}</span>', unsafe_allow_html=True)


def divider():
    st.markdown('<div class="pp-divider"></div>', unsafe_allow_html=True)


def feature_card_html(emoji: str, title: str, description: str) -> str:
    """Returns raw, pre-cleaned HTML for a single feature card (compose in columns)."""
    return _clean(
        f"""
        <div class="pp-feature-card">
            <div class="pp-emoji">{emoji}</div>
            <h4>{title}</h4>
            <p>{description}</p>
        </div>
        """
    )


def stat_html(number: str, label: str) -> str:
    return _clean(
        f"""
        <div class="pp-stat">
            <div class="pp-stat-num">{number}</div>
            <div class="pp-stat-label">{label}</div>
        </div>
        """
    )


def empty_state(icon: str, title: str, message: str):
    st.markdown(
        _clean(
            f"""
            <div class="pp-card" style="text-align:center; padding:3rem 2rem; border-style:dashed;">
                <div style="font-size:2.4rem; margin-bottom:0.6rem;">{icon}</div>
                <h3 style="margin-bottom:0.4rem;">{title}</h3>
                <p style="color:#6B7280; margin:0;">{message}</p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def model_incompatibility_alert(reason: str, recommended_models: list = None):
    """Premium-styled 'selected model not recommended / not compatible'
    alert (TASK 1 pre-flight validation). Reuses the existing .pp-card and
    .pp-badge.danger classes already defined in style.css — no new CSS,
    no change to the design system, just a consistent way to present a
    validation failure instead of a raw exception.
    """
    recommended_models = recommended_models or []
    recs_html = "".join(
        f'<div style="margin:0.25rem 0;">✓ {html.escape(m)}</div>' for m in recommended_models
    )
    st.markdown(
        _clean(
            f"""
            <div class="pp-card" style="border-left:4px solid #EF4444;">
                <span class="pp-badge danger">⚠️ Selected Model Not Recommended</span>
                <p style="margin:0.9rem 0 0.4rem 0; color:var(--text-muted);">
                    The selected algorithm is not suitable for your current dataset.
                </p>
                <p style="margin:0 0 0.6rem 0;"><strong>Reason:</strong><br>{html.escape(reason)}</p>
                {"<p style='margin:0 0 0.3rem 0;'><strong>Recommended Models:</strong></p>" + recs_html if recs_html else ""}
                <p style="margin:0.8rem 0 0 0; color:var(--text-muted);">
                    Please choose one of the recommended models and try again.
                </p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def training_failed_alert():
    """Premium-styled 'training failed unexpectedly' alert (TASK 1,
    second branch). Shown when pipeline.fit() raised something pre-flight
    validation didn't anticipate — the real exception is logged server-side
    (see utils.model_trainer.ModelTrainingError), never shown here."""
    st.markdown(
        _clean(
            """
            <div class="pp-card" style="border-left:4px solid #EF4444;">
                <span class="pp-badge danger">⚠️ Model Training Failed</span>
                <p style="margin:0.9rem 0 0.6rem 0; color:var(--text-muted);">
                    The selected model could not be trained on the uploaded dataset.
                </p>
                <p style="margin:0 0 0.3rem 0;"><strong>Possible reasons:</strong></p>
                <div style="margin:0.25rem 0;">• Unsupported target variable</div>
                <div style="margin:0.25rem 0;">• Invalid feature values</div>
                <div style="margin:0.25rem 0;">• Insufficient training samples</div>
                <div style="margin:0.25rem 0;">• Incompatible dataset</div>
                <p style="margin:0.8rem 0 0 0; color:var(--text-muted);">
                    Please review your dataset or choose another algorithm.
                </p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def prediction_failed_alert(context: str = "Prediction"):
    """Premium-styled prediction-failure alert, mirroring
    training_failed_alert() for the Prediction page. The real exception is
    logged server-side, never shown here."""
    st.markdown(
        _clean(
            f"""
            <div class="pp-card" style="border-left:4px solid #EF4444;">
                <span class="pp-badge danger">⚠️ {html.escape(context)} Failed</span>
                <p style="margin:0.9rem 0 0.6rem 0; color:var(--text-muted);">
                    We couldn't complete this {html.escape(context.lower())}.
                </p>
                <p style="margin:0 0 0.3rem 0;"><strong>Possible reasons:</strong></p>
                <div style="margin:0.25rem 0;">• Input values don't match the format the model was trained on</div>
                <div style="margin:0.25rem 0;">• Missing or invalid required columns</div>
                <div style="margin:0.25rem 0;">• Unexpected data type in one or more fields</div>
                <p style="margin:0.8rem 0 0 0; color:var(--text-muted);">
                    Please check your input and try again.
                </p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def footer():
    """Single, quiet footer credit shown once at the bottom of each page."""
    st.markdown(
        _clean(
            """
            <div class="pp-app-footer">
                <div class="pp-footer-copy">© 2026 Student Performance AI</div>
                <div class="pp-footer-credit">Designed &amp; Developed by <strong>Mohamed Shahjan</strong></div>
                <div class="pp-footer-meta">B.E. Computer Science Engineering &nbsp;|&nbsp; Second Year</div>
                <div class="pp-footer-stack">
                    <span>🐍 Python</span>
                    <span>🎈 Streamlit</span>
                    <span>🧠 Scikit-learn</span>
                    <span>📈 Plotly</span>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def splash_credit():
    """A small, elegant one-line credit — intended for the landing page only."""
    st.markdown(
        '<div class="pp-splash-credit">Built with <span>❤️</span> by Mohamed Shahjan</div>',
        unsafe_allow_html=True,
    )


def developer_card():
    """Premium developer profile card for the About page."""
    st.markdown(
        _clean(
            """
            <div class="pp-dev-card">
                <div class="pp-dev-header">
                    <div class="pp-dev-avatar">👨‍💻</div>
                    <div>
                        <p class="pp-dev-name">Mohamed Shahjan</p>
                        <div class="pp-dev-role">AI &amp; Machine Learning Developer</div>
                        <div class="pp-dev-role-secondary">Game Development Enthusiast</div>
                        <div class="pp-dev-edu">B.E. Computer Science Engineering · Second Year Student</div>
                    </div>
                </div>
                <div class="pp-dev-section-label">Specialization</div>
                <div class="pp-dev-tags">
                    <span>Artificial Intelligence</span>
                    <span>Machine Learning</span>
                    <span>Data Science</span>
                    <span>Python Development</span>
                    <span>Game Development</span>
                    <span>Streamlit Applications</span>
                </div>
                <div class="pp-dev-section-label">About</div>
                <p class="pp-dev-about">
                    "I am a passionate B.E. Computer Science Engineering (Second Year) student with a strong
                    interest in Artificial Intelligence, Machine Learning, Data Science, Python Development,
                    and Game Development. I enjoy building intelligent applications, modern software solutions,
                    and immersive gaming experiences that solve real-world problems while continuously learning
                    emerging technologies. My goal is to become a professional AI Engineer and Game Developer."
                </p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def plotly_theme_layout(font_color: str = "#1F2937") -> dict:
    """
    Shared Plotly layout overrides so every chart in the app matches the
    light premium theme and renders identically regardless of a Streamlit
    Cloud viewer's Light/Dark/"Use system setting" theme choice.

    Why this is needed: st.plotly_chart() applies Streamlit's own active
    theme on top of a figure by default (its theme= argument defaults to
    "streamlit"), which restyles the figure's colors to match whatever
    theme the current viewer has selected — silently overriding
    template="plotly_white" set in Python. Callers must pass
    theme=None to st.plotly_chart() to opt out of that behavior and let
    the figure's own explicit styling (this dict) take effect instead:

        fig.update_layout(**plotly_theme_layout())
        st.plotly_chart(fig, use_container_width=True, theme=None)

    Returns a dict suitable for `fig.update_layout(**plotly_theme_layout())`.
    """
    return dict(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=font_color, family="Inter, 'Plus Jakarta Sans', sans-serif"),
    )
