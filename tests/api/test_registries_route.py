class TestRegistriesRoute:

    def test_registries_endpoint_returns_200(self, client):
        response = client.get("/registries")
        assert response.status_code == 200

    def test_registries_response_has_all_sections(self, client):
        data = client.get("/registries").get_json()

        assert "strategies" in data
        assert "stop_loss" in data
        assert "take_profit" in data
        assert "position_sizing" in data

    def test_strategies_contains_all_entries(self, client):
        data = client.get("/registries").get_json()
        keys = [s["key"] for s in data["strategies"]]

        assert "sma_crossover" in keys
        assert "ema_crossover" in keys
        assert "macd_crossover" in keys
        assert "rsi_mean_reversion" in keys
        assert "bb_bounce" in keys

    def test_strategy_entry_has_label_and_parameters(self, client):
        data = client.get("/registries").get_json()

        for entry in data["strategies"]:
            assert "key" in entry
            assert "label" in entry
            assert "parameters" in entry
            assert isinstance(entry["parameters"], list)

            for param in entry["parameters"]:
                assert "key" in param
                assert "label" in param
                assert "type" in param
                assert "default" in param

    def test_sma_crossover_metadata_matches_expected(self, client):
        data = client.get("/registries").get_json()
        sma = next(s for s in data["strategies"] if s["key"] == "sma_crossover")

        assert sma["label"] == "SMA Crossover"
        assert len(sma["parameters"]) == 2

        short = sma["parameters"][0]
        assert short["key"] == "short_period"
        assert short["default"] == 20
        assert short["min"] == 1

        long = sma["parameters"][1]
        assert long["key"] == "long_period"
        assert long["default"] == 50

    def test_bb_bounce_has_step_on_std_multiplier(self, client):
        data = client.get("/registries").get_json()
        bb = next(s for s in data["strategies"] if s["key"] == "bb_bounce")
        std = next(p for p in bb["parameters"] if p["key"] == "std_multiplier")

        assert std["step"] == 0.1
        assert std["default"] == 2.0

    # ── Stop-loss registry ───────────────────────────────────

    def test_stop_loss_contains_all_entries(self, client):
        data = client.get("/registries").get_json()
        keys = [s["key"] for s in data["stop_loss"]]

        assert "fixed_percentage" in keys
        assert "fixed_price_offset" in keys
        assert "trailing_stop" in keys

    def test_stop_loss_fixed_percentage_has_display_scale(self, client):
        data = client.get("/registries").get_json()
        entry = next(s for s in data["stop_loss"] if s["key"] == "fixed_percentage")
        param = entry["parameters"][0]

        assert param["key"] == "percent"
        assert param["display_scale"] == 100
        assert param["default"] == 5

    # ── Take-profit registry ─────────────────────────────────

    def test_take_profit_contains_all_entries(self, client):
        data = client.get("/registries").get_json()
        keys = [s["key"] for s in data["take_profit"]]

        assert "fixed_percentage" in keys
        assert "fixed_amount" in keys

    def test_take_profit_fixed_amount_has_no_display_scale(self, client):
        data = client.get("/registries").get_json()
        entry = next(s for s in data["take_profit"] if s["key"] == "fixed_amount")
        param = entry["parameters"][0]

        assert param["key"] == "amount"
        assert "display_scale" not in param

    # ── Position-sizing registry ─────────────────────────────

    def test_position_sizing_contains_expected_entries(self, client):
        data = client.get("/registries").get_json()
        keys = [s["key"] for s in data["position_sizing"]]

        assert "fixed_percentage" in keys
        assert "fixed_amount" in keys
        assert "fixed_shares" in keys
        assert "risk_based" in keys
        assert "kelly_criterion" in keys

    def test_position_sizing_excludes_all_in(self, client):
        data = client.get("/registries").get_json()
        keys = [s["key"] for s in data["position_sizing"]]

        assert "all_in" not in keys

    def test_kelly_criterion_has_three_parameters(self, client):
        data = client.get("/registries").get_json()
        kelly = next(s for s in data["position_sizing"] if s["key"] == "kelly_criterion")

        assert len(kelly["parameters"]) == 3
        param_keys = [p["key"] for p in kelly["parameters"]]
        assert "win_rate" in param_keys
        assert "win_loss_ratio" in param_keys
        assert "kelly_fraction" in param_keys

    def test_kelly_criterion_display_scale_on_percentages(self, client):
        data = client.get("/registries").get_json()
        kelly = next(s for s in data["position_sizing"] if s["key"] == "kelly_criterion")

        win_rate = next(p for p in kelly["parameters"] if p["key"] == "win_rate")
        assert win_rate["display_scale"] == 100

        ratio = next(p for p in kelly["parameters"] if p["key"] == "win_loss_ratio")
        assert "display_scale" not in ratio

        fraction = next(p for p in kelly["parameters"] if p["key"] == "kelly_fraction")
        assert fraction["display_scale"] == 100
