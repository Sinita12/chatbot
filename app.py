elif st.session_state.page == "GreenScore":
    st.button("← Back to Home", on_click=go, args=("Home",))
    st.title("🌿 GreenScore")    
    # Check if user clicked an alternative product
    if "impact_history" not in st.session_state:
        st.session_state.impact_history = pd.DataFrame(columns=[
            "Product", "Category", "Eco Score",
            "Carbon (kg)", "Water (L)", "Energy (MJ)", "Waste Score"
        ])

    if "logged_keys" not in st.session_state:
        st.session_state.logged_keys = set()


    # -----------------------------
    # Step 7: USER INPUT + DISPLAY
    # -----------------------------
    st.subheader("📸 Scan Product (optional)")
    
    image_file = st.camera_input("Take a photo of the product")
    
    if image_file:
        image = Image.open(image_file)
    
        with st.spinner("Reading packaging text..."):
            all_text = ocr_image(image)
        
        with st.spinner("Identifying product..."):
            detected_name = extract_product_name(all_text)
            matched_name, confidence = fuzzy_match_product(detected_name, summary_df)
        
        st.success(f"Detected: {matched_name}")
        st.session_state.selected_product = matched_name
            
        # Decide preselected product (scan > alternative > none)
        
        # -----------------------------
        # Decide preselected product
        # Priority: scanned > alternative > previous selection
        # -----------------------------
    # -----------------------------
    # PRODUCT SEARCH (ALWAYS VISIBLE)
    # -----------------------------
# -----------------------------
# PRODUCT SEARCH (ALWAYS VISIBLE)
# -----------------------------
    product_options = sorted(summary_df['name'].unique())
    
    # Priority:
    # 1. Clicked alternative
    # 2. Scanned product
    # 3. Previous selection
    
    preselected_product = None
    
    if "selected_alternative" in st.session_state:
        preselected_product = st.session_state.selected_alternative
    elif "selected_product" in st.session_state:
        preselected_product = st.session_state.selected_product
    
    if preselected_product in product_options:
        default_index = product_options.index(preselected_product)
    else:
        default_index = 0
    
    product_input = st.selectbox(
        "🔍 Search for a product",
        options=product_options,
        index=default_index,
        placeholder="Start typing to search..."
    )
    
    # Clear after applying
    if "selected_alternative" in st.session_state:
        del st.session_state["selected_alternative"]

    if product_input:
        result = summary_df[summary_df['name'] == product_input]
        st.session_state.selected_product = product_input
    
        if result.empty:
            st.error("❌ Product not found in database.")
        else:
            r = result.iloc[0]
            log_key = f"{product_input}_{r['eco_score']}"

            if log_key not in st.session_state.logged_keys:
                st.session_state.impact_history.loc[len(st.session_state.impact_history)] = {
                    "Product": product_input,
                    "Category": r["category"],
                    "Eco Score": r["eco_score"],
                    "Carbon (kg)": r["total_carbon_kg"],
                    "Water (L)": r["total_water_L"],
                    "Energy (MJ)": r["total_energy_MJ"],
                    "Waste Score": r["total_waste_score"]
                }
                st.session_state.logged_keys.add(log_key)
    
            st.divider()
            
            # ---------- ECO SCORE ----------
            st.markdown("### 🌿 Eco Score")
            
            # Create a more visually appealing score display
            score_col1, score_col2 = st.columns([2, 3])
            
            with score_col1:
                # Large score display
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #2d5016 0%, #3d6b1f 100%);
                        border-radius: 18px;
                        padding: 30px;
                        text-align: center;
                        box-shadow: 0 8px 20px rgba(45, 80, 22, 0.3);
                    ">
                        <h1 style="color: #f5f1e8; margin: 0; font-size: 4em;">{r['eco_score']}</h1>
                        <p style="color: #c5d4b8; margin: 5px 0 0 0; font-size: 1.1em;">out of 100</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with score_col2:
                # Score interpretation
                if r['eco_score'] >= 80:
                    badge_color = "#2d5016"
                    badge_text = "Excellent"
                    emoji = "🌟"
                elif r['eco_score'] >= 60:
                    badge_color = "#4d7b2f"
                    badge_text = "Good"
                    emoji = "👍"
                elif r['eco_score'] >= 40:
                    badge_color = "#d4a373"
                    badge_text = "Moderate"
                    emoji = "⚠️"
                else:
                    badge_color = "#a85232"
                    badge_text = "Needs Improvement"
                    emoji = "❗"
                
                st.markdown(f"""
                    <div style="padding: 20px 0;">
                        <div style="
                            background-color: {badge_color};
                            color: #f5f1e8;
                            padding: 15px 25px;
                            border-radius: 14px;
                            display: inline-block;
                            font-size: 1.3em;
                            font-weight: bold;
                            margin-bottom: 15px;
                            box-shadow: 0 4px 12px rgba(45, 80, 22, 0.2);
                        ">
                            {emoji} {badge_text}
                        </div>
                        <p style="color: #9cb380; margin-top: 10px; line-height: 1.6;">
                            This score reflects the overall environmental impact across carbon, water, energy, and waste metrics.
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Progress bar with custom styling
            st.markdown(f"""
                <div style="margin: 20px 0;">
                    <div style="
                        background-color: #3d4a35;
                        border-radius: 12px;
                        height: 14px;
                        overflow: hidden;
                    ">
                        <div style="
                            background: linear-gradient(90deg, #2d5016 0%, #4d7b2f 50%, #7c9070 100%);
                            width: {r['eco_score']}%;
                            height: 100%;
                            border-radius: 12px;
                            transition: width 0.5s ease;
                        "></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
            st.divider()
    
            # ---------- METRICS ----------
            st.markdown("### 📊 Environmental Impact Breakdown")
            
            col1, col2, col3, col4 = st.columns(4)
    
            with col1:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #f5f1e8 0%, #faf8f3 100%);
                        border-left: 4px solid #d4a373;
                        border-radius: 12px;
                        padding: 20px 15px;
                        text-align: center;
                        box-shadow: 0 4px 12px rgba(45, 80, 22, 0.1);
                    ">
                        <div style="font-size: 2em; margin-bottom: 10px;">🌫</div>
                        <div style="color: #5d4e37; font-size: 0.85em; margin-bottom: 5px; font-weight: 600;">Carbon Footprint</div>
                        <div style="color: #2d1810; font-size: 1.5em; font-weight: bold;">{r['total_carbon_kg']}</div>
                        <div style="color: #5d4e37; font-size: 0.75em;">kg CO₂e</div>
                    </div>
                """, unsafe_allow_html=True)
    
            with col2:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8f3 100%);
                        border-left: 4px solid #4d7b2f;
                        border-radius: 12px;
                        padding: 20px 15px;
                        text-align: center;
                        box-shadow: 0 4px 12px rgba(45, 80, 22, 0.1);
                    ">
                        <div style="font-size: 2em; margin-bottom: 10px;">💧</div>
                        <div style="color: #2d5016; font-size: 0.85em; margin-bottom: 5px; font-weight: 600;">Water Usage</div>
                        <div style="color: #1a3d0f; font-size: 1.5em; font-weight: bold;">{r['total_water_L']}</div>
                        <div style="color: #2d5016; font-size: 0.75em;">Liters</div>
                    </div>
                """, unsafe_allow_html=True)
    
            with col3:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #fff9e6 0%, #fffcf0 100%);
                        border-left: 4px solid #d4a373;
                        border-radius: 12px;
                        padding: 20px 15px;
                        text-align: center;
                        box-shadow: 0 4px 12px rgba(45, 80, 22, 0.1);
                    ">
                        <div style="font-size: 2em; margin-bottom: 10px;">⚡</div>
                        <div style="color: #6b4423; font-size: 0.85em; margin-bottom: 5px; font-weight: 600;">Energy Use</div>
                        <div style="color: #3d2815; font-size: 1.5em; font-weight: bold;">{r['total_energy_MJ']}</div>
                        <div style="color: #6b4423; font-size: 0.75em;">MJ</div>
                    </div>
                """, unsafe_allow_html=True)
    
            with col4:
                st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #f5f1e8 0%, #faf8f3 100%);
                        border-left: 4px solid #7c9070;
                        border-radius: 12px;
                        padding: 20px 15px;
                        text-align: center;
                        box-shadow: 0 4px 12px rgba(45, 80, 22, 0.1);
                    ">
                        <div style="font-size: 2em; margin-bottom: 10px;">🗑</div>
                        <div style="color: #3d4a35; font-size: 0.85em; margin-bottom: 5px; font-weight: 600;">Waste Impact</div>
                        <div style="color: #1a2318; font-size: 1.5em; font-weight: bold;">{r['total_waste_score']}</div>
                        <div style="color: #3d4a35; font-size: 0.75em;">Score</div>
                    </div>
                """, unsafe_allow_html=True)

                        # ---------- INGREDIENT FLAGS (only show present ones) ----------
            st.markdown("### 🧪 Ingredient Flags")
            
            flag_defs = [
                {
                    "key": "microplastics",
                    "title": "Microplastics",
                    "emoji": "🧬",
                    "present": int(r["microplastics"]) == 1,
                    "why": "Microplastics can persist in waterways and harm aquatic life when washed down drains."
                },
                {
                    "key": "silicones",
                    "title": "Silicones",
                    "emoji": "🧴",
                    "present": int(r["silicones"]) == 1,
                    "why": "Some silicones are persistent and can contribute to long-lasting pollution in the environment."
                },
                {
                    "key": "petroleum",
                    "title": "Petroleum-derived",
                    "emoji": "🛢️",
                    "present": int(r["petroleum"]) == 1,
                    "why": "Petroleum-based ingredients come from fossil fuels, increasing reliance on non-renewable resources."
                },
            ]
            
            present_flags = [f for f in flag_defs if f["present"]]
            
            if present_flags:
                cols = st.columns(len(present_flags))
                for col, flag in zip(cols, present_flags):
                    with col:
                        st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, #fff4e6 0%, #f5f1e8 100%);
                                border-left: 4px solid #d4a373;
                                border-radius: 12px;
                                padding: 18px 14px;
                                box-shadow: 0 4px 12px rgba(45, 80, 22, 0.10);
                                min-height: 155px;
                            ">
                                <div style="font-size: 1.8em; margin-bottom: 6px;">{flag["emoji"]}</div>
                                <div style="font-weight: 700; font-size: 1.05em; color: #1a2318;">{flag["title"]} — Present</div>
                                <div style="margin-top: 10px; font-size: 0.9em; line-height: 1.45; color: #3d4a35;">
                                    {flag["why"]}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("✅ No ingredient red flags detected for this product (based on our database).")
    
            st.markdown("<br>", unsafe_allow_html=True)
    
            # ---------- OPTIONAL DETAILS ----------
            with st.expander("📊 View detailed data"):
                st.dataframe(result, use_container_width=True)

            # =============================
            # GREENER ALTERNATIVES
            # =============================
            st.subheader("🌿 Greener Alternatives")
            st.caption("Click any product to view its full eco score")
            
            alternatives = get_greener_alternatives(product_input, summary_df, max_alternatives=5)
            
            if alternatives:
                for alt in alternatives:
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(
                            f"""
                            <div style="
                                background: linear-gradient(135deg, #e8f5e9 0%, #f5f1e8 100%);
                                border-left: 5px solid #2d5016;
                                border-radius: 14px;
                                padding: 18px;
                                margin-bottom: 14px;
                                cursor: pointer;
                                transition: all 0.3s ease;
                                box-shadow: 0 4px 12px rgba(45, 80, 22, 0.15);
                            ">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <strong style="color:#1a3d0f; font-size:17px;">{alt['name']}</strong><br>
                                        <span style="color:#4d7b2f; font-size:14px;">✨ {alt['improvement']}</span>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="color:#2d5016; font-size:26px; font-weight:700;">{alt['eco_score']}</div>
                                        <div style="color:#5d4e37; font-size:12px;">+{alt['score_diff']:.1f} points</div>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    with col2:
                        if st.button("View →", key=f"view_{alt['name']}", use_container_width=True):
                            st.session_state['selected_alternative'] = alt['name']
                            st.rerun()
            else:
                st.info("🎉 Great choice! This is already one of the greenest options in its category.")
            # =============================
# AI DEEP DIVE EXPLANATION
# =============================
st.divider()
st.subheader("🤖 AI Insight: Understand This Eco Score")

st.caption(
    "Get a deeper explanation of *why* this product scored the way it did, "
    "and what better purchase choices you can make next."
)

# Init OpenAI client (reuse your key)
client = OpenAI(api_key=st.secrets["OpenAIKey"])

if st.button("🧠 Ask AI to explain this Eco Score", use_container_width=True):

    with st.spinner("Analyzing this product’s environmental impact... 🌍"):

        # Build a product-specific prompt
        ai_prompt = f"""
You are an environmental impact analyst inside a sustainability app.

Explain the Eco Score for the following product in a clear, structured way.

PRODUCT DETAILS:
- Name: {product_input}
- Category: {r['category']}
- Eco Score: {r['eco_score']} / 100
- Carbon Footprint: {r['total_carbon_kg']} kg CO₂e
- Water Usage: {r['total_water_L']} L
- Energy Use: {r['total_energy_MJ']} MJ
- Waste Impact Score: {r['total_waste_score']}

INGREDIENT FLAGS:
- Microplastics present: {bool(int(r['microplastics']))}
- Silicones present: {bool(int(r['silicones']))}
- Petroleum-derived ingredients present: {bool(int(r['petroleum']))}

INSTRUCTIONS:
1. Explain WHY the eco score is at this level (not generic).
2. Clearly state which factor hurts the score most.
3. Mention ingredient flags only if present and why they matter.
4. Suggest 2–3 BETTER PURCHASE ACTIONS (not lifestyle tips).
5. Suggest what to look for in greener alternatives next time.
6. Keep it concise, specific, and easy to understand.
7. Do NOT give generic advice like “save water” or “turn off lights”.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.4,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You explain product environmental impacts clearly and practically. "
                        "Focus only on purchase-related sustainability decisions."
                    )
                },
                {"role": "user", "content": ai_prompt}
            ]
        )

        ai_reply = response.choices[0].message.content

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #f5f1e8 0%, #ffffff 100%);
                border-left: 6px solid #2d5016;
                border-radius: 16px;
                padding: 22px;
                margin-top: 18px;
                box-shadow: 0 6px 18px rgba(45, 80, 22, 0.15);
            ">
                <div style="font-size: 1.1em; line-height: 1.65; color: #1a2318;">
                    {ai_reply}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
