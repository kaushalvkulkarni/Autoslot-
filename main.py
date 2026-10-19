import flet as ft

# --- THEME PALETTE (80/20 GLOW RULE) ---
BG_DEEP_NAVY = "#050A14"       # 80% Abyssal navy-black background
CARD_DARK_GLASS = "#0B1324"    # Translucent dark slate for slot cards
CYAN_NEON = "#00E5FF"          # Electric cyan accent
CYAN_DIM_BORDER = "#1A5F7A"    # Crisp 1px border for standard cards
TEXT_WHITE = "#F0F6FC"         # Ice-white readable text
TEXT_MUTED = "#8B949E"         # Muted grey sub-labels
EMERALD_GREEN = "#00E676"      # Active / Free status accent
AMBER_WARN = "#FFB300"         # Blackout / Shield badge accent

TIME_OPTIONS = [
    "06:00 AM", "06:30 AM", "07:00 AM", "07:30 AM", "08:00 AM", "08:30 AM",
    "09:00 AM", "09:30 AM", "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM",
    "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM", "06:00 PM", "06:30 PM",
    "07:00 PM", "07:30 PM", "08:00 PM", "08:30 PM", "09:00 PM", "09:30 PM",
    "10:00 PM", "10:30 PM", "11:00 PM"
]

BACKUP_MAP = {
    "09:00 PM": "08:30 PM",
    "09:30 PM": "09:00 PM",
    "10:00 PM": "09:30 PM",
    "10:30 PM": "10:00 PM",
    "11:00 PM": "10:30 PM",
}


def main(page: ft.Page):
    page.title = "AutoSlot • System Calibration"
    page.bgcolor = BG_DEEP_NAVY
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.DARK

    # --- STATE STORE (READY FOR SUPABASE SYNC) ---
    user_slots = {
        "workout_mode": "Morning",
        "workout_start": "06:30 AM",
        "workout_end": "07:30 AM",
        "meals": ["08:30 AM", "01:30 PM", "08:30 PM"],
        "role_mode": "College",
        "busy_start": "09:00 AM",
        "busy_end": "04:00 PM",
        "deep_work_start": "07:00 PM",
        "deep_work_end": "08:30 PM",
        "self_time_start": "09:30 PM",
        "self_time_end": "10:30 PM",
        "backup_shift_slot": "09:00 PM",
        "battery_shield_enabled": True,
    }

    # Helper to build compact time dropdowns
    def make_time_dropdown(default_val, on_change_fn=None):
        return ft.Dropdown(
            value=default_val,
            options=[ft.dropdown.Option(t) for t in TIME_OPTIONS],
            width=130,
            text_size=13,
            color=TEXT_WHITE,
            bgcolor=BG_DEEP_NAVY,
            border_color=CYAN_DIM_BORDER,
            focused_border_color=CYAN_NEON,
            border_radius=8,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=6),
            on_change=on_change_fn,
        )

    # Helper to wrap each of the 5 sections in a clean 1px cyan glass card
    def make_slot_card(content_col, is_blackout=False):
        return ft.Container(
            content=content_col,
            bgcolor=CARD_DARK_GLASS,
            padding=16,
            border_radius=12,
            border=ft.border.all(1, AMBER_WARN if is_blackout else CYAN_DIM_BORDER),
            col={"xs": 12, "md": 6, "lg": 4},  # Stacks on Phone, Grid on Tablet!
        )

    # =========================================================================
    # 1. WORKOUT WINDOW (With 1-Tap [☀️ Morn | 🌙 Eve] Toggle)
    # =========================================================================
    workout_start_dd = make_time_dropdown(user_slots["workout_start"])
    workout_end_dd = make_time_dropdown(user_slots["workout_end"])

    def toggle_workout_mode(mode):
        user_slots["workout_mode"] = mode
        if mode == "Morning":
            workout_start_dd.value = "06:30 AM"
            workout_end_dd.value = "07:30 AM"
            morn_btn.bgcolor = CYAN_NEON
            morn_btn.content.color = BG_DEEP_NAVY
            eve_btn.bgcolor = BG_DEEP_NAVY
            eve_btn.content.color = TEXT_MUTED
        else:
            workout_start_dd.value = "05:30 PM"
            workout_end_dd.value = "06:30 PM"
            eve_btn.bgcolor = CYAN_NEON
            eve_btn.content.color = BG_DEEP_NAVY
            morn_btn.bgcolor = BG_DEEP_NAVY
            morn_btn.content.color = TEXT_MUTED
        page.update()

    morn_btn = ft.Container(
        content=ft.Text("☀️ Morn", size=12, weight=ft.FontWeight.BOLD, color=BG_DEEP_NAVY),
        bgcolor=CYAN_NEON,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        border_radius=6,
        on_click=lambda _: toggle_workout_mode("Morning"),
    )
    eve_btn = ft.Container(
        content=ft.Text("🌙 Eve", size=12, weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
        bgcolor=BG_DEEP_NAVY,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        border_radius=6,
        on_click=lambda _: toggle_workout_mode("Evening"),
    )

    workout_card = make_slot_card(
        ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("💪 WORKOUT WINDOW", size=14, weight=ft.FontWeight.BOLD, color=CYAN_NEON),
                        ft.Row(spacing=4, controls=[morn_btn, eve_btn]),
                    ],
                ),
                ft.Text("Active Auto-Slot • AI books spoken workouts here", size=11, color=TEXT_MUTED),
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        workout_start_dd,
                        ft.Text("to", color=TEXT_MUTED, size=12),
                        workout_end_dd,
                    ],
                ),
            ],
        )
    )

    # =========================================================================
    # 2. MEALS / DIET REMINDERS (Point-in-Time Pings)
    # =========================================================================
    meal_1_dd = make_time_dropdown("08:30 AM")
    meal_2_dd = make_time_dropdown("01:30 PM")
    meal_3_dd = make_time_dropdown("08:30 PM")

    meals_card = make_slot_card(
        ft.Column(
            spacing=10,
            controls=[
                ft.Text("🥗 MEALS / DIET PINGS", size=14, weight=ft.FontWeight.BOLD, color=CYAN_NEON),
                ft.Text("Point-in-Time Pings • Instant check-off into Collection Tube", size=11, color=TEXT_MUTED),
                ft.Row(
                    wrap=True,
                    spacing=8,
                    run_spacing=8,
                    controls=[meal_1_dd, meal_2_dd, meal_3_dd],
                ),
            ],
        )
    )

    # =========================================================================
    # 3. COLLEGE / OFFICE / SCHOOL / WORK (AI Blackout Zone + Role Picker)
    # =========================================================================
    busy_title = ft.Text("🎓 COLLEGE HOURS (BUSY ZONE)", size=14, weight=ft.FontWeight.BOLD, color=AMBER_WARN)
    busy_start_dd = make_time_dropdown(user_slots["busy_start"])
    busy_end_dd = make_time_dropdown(user_slots["busy_end"])

    role_presets = {
        "College": ("🎓 COLLEGE HOURS (BUSY ZONE)", "09:00 AM", "04:00 PM"),
        "Office":  ("🏢 OFFICE HOURS (BUSY ZONE)",  "09:00 AM", "05:00 PM"),
        "School":  ("🎒 SCHOOL HOURS (BUSY ZONE)",  "08:00 AM", "02:30 PM"),
        "Work":    ("💻 WORK HOURS (BUSY ZONE)",    "09:30 AM", "05:30 PM"),
    }
    role_chips = {}

    def select_role(role_key):
        user_slots["role_mode"] = role_key
        title_str, s_time, e_time = role_presets[role_key]
        busy_title.value = title_str
        busy_start_dd.value = s_time
        busy_end_dd.value = e_time
        for k, chip in role_chips.items():
            is_sel = (k == role_key)
            chip.bgcolor = AMBER_WARN if is_sel else BG_DEEP_NAVY
            chip.content.color = BG_DEEP_NAVY if is_sel else TEXT_MUTED
        page.update()

    for r_key, r_label in [("College", "🎓 College"), ("Office", "🏢 Office"), ("School", "🎒 School"), ("Work", "💻 Work")]:
        is_default = (r_key == "College")
        chip = ft.Container(
            content=ft.Text(r_label, size=11, weight=ft.FontWeight.BOLD, color=BG_DEEP_NAVY if is_default else TEXT_MUTED),
            bgcolor=AMBER_WARN if is_default else BG_DEEP_NAVY,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=6,
            border=ft.border.all(1, AMBER_WARN),
            on_click=lambda _, rk=r_key: select_role(rk),
        )
        role_chips[r_key] = chip

    busy_card = make_slot_card(
        ft.Column(
            spacing=10,
            controls=[
                busy_title,
                ft.Row(wrap=True, spacing=6, controls=list(role_chips.values())),
                ft.Text("🚫 AI Blackout Zone • Zero alerts or tasks scheduled here", size=11, color=TEXT_MUTED),
                ft.Row(
                    controls=[
                        busy_start_dd,
                        ft.Text("to", color=TEXT_MUTED, size=12),
                        busy_end_dd,
                    ]
                ),
            ],
        ),
        is_blackout=True,
    )

    # =========================================================================
    # 4. DEEP WORK / ASSIGNMENTS (25m Pomodoro Auto-Slicing Slot)
    # =========================================================================
    deep_start_dd = make_time_dropdown(user_slots["deep_work_start"])
    deep_end_dd = make_time_dropdown(user_slots["deep_work_end"])

    deep_work_card = make_slot_card(
        ft.Column(
            spacing=10,
            controls=[
                ft.Text("⚡ DEEP WORK / ASSIGNMENTS", size=14, weight=ft.FontWeight.BOLD, color=CYAN_NEON),
                ft.Text("Active Auto-Slot • AI slices deadlines into 25m sprints (1/3)", size=11, color=TEXT_MUTED),
                ft.Row(
                    controls=[
                        deep_start_dd,
                        ft.Text("to", color=TEXT_MUTED, size=12),
                        deep_end_dd,
                    ]
                ),
            ],
        )
    )

    # =========================================================================
    # 5. SELF TIME + AUTOMATIC BACKUP SHIFT SLOT (30m Before Self Time)
    # =========================================================================
    backup_badge = ft.Text(
        f"🔄 Auto Backup Shift Slot: {user_slots['backup_shift_slot']} (30m before Self Time)",
        size=11,
        weight=ft.FontWeight.BOLD,
        color=EMERALD_GREEN,
    )

    def on_self_time_change(e):
        chosen = self_start_dd.value
        user_slots["self_time_start"] = chosen
        user_slots["backup_shift_slot"] = BACKUP_MAP.get(chosen, "09:00 PM")
        backup_badge.value = f"🔄 Auto Backup Shift Slot: {user_slots['backup_shift_slot']} (30m before Self Time)"
        page.update()

    self_start_dd = make_time_dropdown(user_slots["self_time_start"], on_change_fn=on_self_time_change)
    self_end_dd = make_time_dropdown(user_slots["self_time_end"])

    self_time_card = make_slot_card(
        ft.Column(
            spacing=10,
            controls=[
                ft.Text("🎧 SELF TIME (UNWIND)", size=14, weight=ft.FontWeight.BOLD, color=AMBER_WARN),
                ft.Text("🚫 Protected Unwind Zone • Hidden from 'Todays' list", size=11, color=TEXT_MUTED),
                ft.Row(
                    controls=[
                        self_start_dd,
                        ft.Text("to", color=TEXT_MUTED, size=12),
                        self_end_dd,
                    ]
                ),
                backup_badge,
            ],
        ),
        is_blackout=True,
    )

    # =========================================================================
    # SLIDE-UP DRAWER: 1-TAP GOOGLE LINK + BATTERY & OVERLAY SHIELD
    # =========================================================================
    shield_switch = ft.Switch(
        value=True,
        active_color=CYAN_NEON,
        label="Enable Battery & Screen-Takeover Shield (Xiaomi/Vivo/Realme)",
        label_style=ft.TextStyle(size=12, color=TEXT_WHITE),
    )

    def complete_onboarding(e):
        # Collect latest dropdown values into state dictionary
        user_slots["workout_start"] = workout_start_dd.value
        user_slots["workout_end"] = workout_end_dd.value
        user_slots["meals"] = [meal_1_dd.value, meal_2_dd.value, meal_3_dd.value]
        user_slots["busy_start"] = busy_start_dd.value
        user_slots["busy_end"] = busy_end_dd.value
        user_slots["deep_work_start"] = deep_start_dd.value
        user_slots["deep_work_end"] = deep_end_dd.value
        user_slots["self_time_end"] = self_end_dd.value
        user_slots["battery_shield_enabled"] = shield_switch.value

        sign_in_sheet.open = False
        page.snack_bar = ft.SnackBar(
            bgcolor=CARD_DARK_GLASS,
            content=ft.Text(
                f"⚡ System Linked! 15-Day Trial Active • Backup Slot locked at {user_slots['backup_shift_slot']}",
                color=CYAN_NEON,
                weight=ft.FontWeight.BOLD,
            ),
        )
        page.snack_bar.open = True
        page.update()

    sign_in_sheet = ft.BottomSheet(
        bgcolor=CARD_DARK_GLASS,
        content=ft.Container(
            padding=24,
            border=ft.border.only(top=ft.BorderSide(2, CYAN_NEON)),
            content=ft.Column(
                tight=True,
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("⚡ LOCK IN SLOTS & START 15-DAY TRIAL", size=16, weight=ft.FontWeight.BOLD, color=CYAN_NEON),
                    ft.Text(
                        "100% Free for 15 Days • Zero Auto-Debit • Switches to 1-Slot Free Mode on Day 16",
                        size=12,
                        color=TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        bgcolor=BG_DEEP_NAVY,
                        padding=10,
                        border_radius=8,
                        border=ft.border.all(1, CYAN_DIM_BORDER),
                        content=shield_switch,
                    ),
                    ft.Container(
                        width=320,
                        height=48,
                        bgcolor=CYAN_NEON,
                        border_radius=10,
                        alignment=ft.alignment.center,
                        shadow=ft.BoxShadow(blur_radius=16, color=CYAN_NEON, spread_radius=1),
                        on_click=complete_onboarding,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=BG_DEEP_NAVY),
                                ft.Text("G  Tap to Link Google Account", size=14, weight=ft.FontWeight.BOLD, color=BG_DEEP_NAVY),
                            ],
                        ),
                    ),
                ],
            ),
        ),
    )
    page.overlay.append(sign_in_sheet)

    def open_sign_in_drawer(e):
        sign_in_sheet.open = True
        page.update()

    # =========================================================================
    # HEAVY NEON GLOW BUTTON (20% HIGHLIGHT FOCUS)
    # =========================================================================
    save_button = ft.Container(
        width=360,
        height=54,
        bgcolor=CYAN_NEON,
        border_radius=12,
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=22,
            color=CYAN_NEON,
            offset=ft.Offset(0, 0),
        ),
        on_click=open_sign_in_drawer,
        content=ft.Text(
            "⚡ SAVE & START 15-DAY TRIAL",
            size=15,
            weight=ft.FontWeight.BOLD,
            color=BG_DEEP_NAVY,
        ),
    )

    # =========================================================================
    # PAGE ASSEMBLY (AUTOMATIC PHONE PORTRAIT + TABLET LANDSCAPE)
    # =========================================================================
    page.add(
        ft.Column(
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                # Top Header
                ft.Container(
                    width=1100,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text("⚡ SET PREFERRED TIME SLOTS", size=20, weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                                    ft.Text(
                                        "Pre-filled for speed. AI schedules voice tasks in Cyan slots & never disturbs Amber zones.",
                                        size=12,
                                        color=TEXT_MUTED,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                # Responsive Grid (Stacks Vertically on Phone, 2-3 Columns on Tablet)
                ft.Container(
                    width=1100,
                    content=ft.ResponsiveRow(
                        spacing=14,
                        run_spacing=14,
                        controls=[
                            workout_card,
                            meals_card,
                            busy_card,
                            deep_work_card,
                            self_time_card,
                        ],
                    ),
                ),
                # Glowing Save CTA
                ft.Container(
                    padding=ft.padding.only(top=10, bottom=20),
                    content=save_button,
                ),
            ],
        )
    )


ft.app(target=main)
