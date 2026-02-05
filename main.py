elif st.session_state.page == "GreenScore":
    st.button("← Back to Home", on_click=go, args=("Home",))
    st.title("🌿 GreenScore")

    if "impact_history" not in st.session_state:
        st.session_state.impact_history = pd.DataFrame(
            columns=[
                "Product",
                "Category",
                "Eco Score",
                "Carbon (kg)",
                "Water (L)",
                "Energy (MJ)",
                "Waste Score",
            ]
        )

    if "logged_keys" not in st.session_state:
        st.session_state.logged_keys = set()

    st.subheader("📸 Scan Product (optional)")
    image_file = st.camera_input("Take a photo of the product")

    if image_file:
        image = Image.open(image_file)

        with st.spinner("Reading packaging text..."):
            all_text = ocr_image(image)

        with st.spinner("Identifying product..."):
            detected_name = extract_product_name(all_text)
            matched_name, confidence = fuzzy_match_product(
                detected_name, summary_df
            )

        st.success(f"Detected: {matched_name}")
        st.session_state.selected_product = matched_name

    product_options = sorted(summary_df["name"].unique())

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
        placeholder="Start typing to search...",
    )

    if "selected_alternative" in st.session_state:
        del st.session_state["selected_alternative"]

    if product_input:
        result = summary_df[summary_df["name"] == product_input]
        st.session_state.selected_product = product_input

        if result.empty:
            st.error("❌ Product not found in database.")
        else:
            r = result.iloc[0]
            log_key = f"{product_input}_{r['eco_score']}"

            if log_key not in st.session_state.logged_keys:
                st.session_state.impact_history.loc[
                    len(st.session_state.impact_history)
                ] = {
                    "Product": product_input,
                    "Category": r["category"],
                    "Eco Score": r["eco_score"],
                    "Carbon (kg)": r["total_carbon_kg"],
                    "Water (L)": r["total_water_L"],
                    "Energy (MJ)": r["total_energy_MJ"],
                    "Waste Score": r["total_waste_score"],
                }
                st.session_state.logged_keys.add(log_key)

            st.divider()

            st.markdown("### 🌿 Eco Score")

            score_col1, score_col2 = st.columns([2, 3])

            with score_col1:
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, #2d5016 0%, #3d6b1f 100%);
                                border-radius: 18px; padding: 30px; text-align: center;">
                        <h1 style="color:#f5f1e8; margin:0;">{r['eco_score']}</h1>
                        <p style="color:#c5d4b8;">out of 100</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with score_col2:
                if r["eco_score"] >= 80:
                    badge_color, badge_text, emoji = "#2d5016", "Excellent", "🌟"
                elif r["eco_score"] >= 60:
                    badge_color, badge_text, emoji = "#4d7b2f", "Good", "👍"
                elif r["eco_score"] >= 40:
                    badge_color, badge_text, emoji = "#d4a373", "Moderate", "⚠️"
                else:
                    badge_color, badge_text, emoji = (
                        "#a85232",
                        "Needs Improvement",
                        "❗",
                    )

                st.markdown(
                    f"""
                    <div>
                        <div style="background:{badge_color}; color:#f5f1e8;
                                    padding:15px 25px; border-radius:14px;
                                    display:inline-block;">
                            {emoji} {badge_text}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.divider()

            st.markdown("### 📊 Environmental Impact Breakdown")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.write(r["total_carbon_kg"], "kg CO₂e")
            with col2:
                st.write(r["total_water_L"], "L")
            with col3:
                st.write(r["total_energy_MJ"], "MJ")
            with col4:
                st.write(r["total_waste_score"], "Score")

            st.markdown("### 🧪 Ingredient Flags")

            with st.expander("📊 View detailed data"):
                st.dataframe(result, use_container_width=True)

            st.subheader("🌿 Greener Alternatives")
            alternatives = get_greener_alternatives(
                product_input, summary_df, max_alternatives=5
            )

            if alternatives:
                for alt in alternatives:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(alt["name"])
                    with col2:
                        if st.button(
                            "View →",
                            key=f"view_{alt['name']}",
                            use_container_width=True,
                        ):
                            st.session_state[
                                "selected_alternative"
                            ] = alt["name"]
                            st.rerun()
            else:
                st.info(
                    "🎉 Great choice! This is already one of the greenest options."
                )

    st.divider()
    st.subheader("🤖 AI Insight: Understand This Eco Score")

    client = OpenAI(api_key=st.secrets["OpenAIKey"])

    if st.button("🧠 Ask AI to explain this Eco Score", use_container_width=True):
        with st.spinner("Analyzing this product’s environmental impact... 🌍"):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.4,
                messages=[
                    {
                        "role": "system",
                        "content": "You explain product environmental impacts clearly.",
                    },
                    {"role": "user", "content": ai_prompt},
                ],
            )

            ai_reply = response.choices[0].message.content

            st.markdown(ai_reply)
