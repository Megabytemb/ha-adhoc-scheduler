# Adhoc Scheduler for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

**Adhoc Scheduler** is a powerful custom integration for Home Assistant that allows you to schedule actions to run at a later time. Unlike the standard `delay` action in automations, schedules created with Adhoc Scheduler are **persistent**, **non-blocking**, and **manageable**.

---

## ⚡ Why use this over the built-in `delay`?

The native `delay` action in Home Assistant scripts and automations has significant limitations for long-running tasks:

1.  **Persistence (The Big One):** If you use a standard `delay: "01:00:00"` and Home Assistant restarts (or crashes) during that hour, **the automation stops dead**. The subsequent actions will _never_ run. Adhoc Scheduler saves your schedules to disk. If HA restarts, your scheduled actions are reloaded and will still fire on time. If HA was down when your scheduled action was due to fire, it fires straight away when HA starts.
2.  **Non-Blocking Execution:** A standard script with a delay remains "running" for the duration. Adhoc Scheduler works on a "fire-and-forget" basis. Your automation triggers the schedule and finishes immediately, freeing up resources and keeping your running script counts low.
3.  **Manageability:** You can assign IDs to your schedules. This allows you to **cancel** a pending action if plans change (e.g., "Turn off lights in 10 minutes," but then motion is detected, so you cancel the timer).
4.  **Observability:** Every scheduled action creates a clear entry in the Logbook when it triggers, making debugging easier.

---

## ✨ Features

- **Flexible Scheduling:** Run actions after a specific **delay** (e.g., "in 30 minutes") or at a specific **time** (e.g., "at 8:00 PM").
- **Reboot Resilient:** Schedules are stored locally. A reboot won't kill your timers.
- **De-duplication:** Use an `id` to ensure only one instance of a schedule exists (e.g., constantly resetting a "turn off" timer).
- **Cancellation:** Easily delete a scheduled action using its `id`.
- **Logbook Integration:** See exactly when your scheduled actions fire.

---

## 📥 Installation

### Option 1: HACS (Recommended)

1.  Open **HACS** in Home Assistant.
2.  Go to **Integrations** > **Explore & Download Repositories**.
3.  Click on the three dots in the top right corner and select "Custom Repositories."
4.  Add the URL `https://github.com/Megabytemb/ha-adhoc-scheduler` for this repository, select "Integration" as the category, and click on "Add."
5.  Navigate back to the **Integrations** tab, search for **Adhoc Scheduler** and click **Download**.
6.  Restart Home Assistant.
7.  Go to **Settings** > **Devices & Services** > **Add Integration**.
8.  Search for **Adhoc Scheduler** and select it to finish setup.

### Option 2: Manual Installation

1.  Download the `adhoc_scheduler` folder from the [latest release](https://github.com/Megabytemb/ha-adhoc-scheduler/releases).
2.  Copy the `adhoc_scheduler` folder into your Home Assistant `custom_components` directory.
3.  Restart Home Assistant.
4.  Go to **Settings** > **Devices & Services** > **Add Integration**.
5.  Search for **Adhoc Scheduler** and select it.

---

## 🛠️ Usage

This integration adds two services to Home Assistant.

### 1. `adhoc_scheduler.schedule`

Schedules an action to run later.

**Parameters:**

| Field          | Type     | Required | Description                                                                                        |
| :------------- | :------- | :------- | :------------------------------------------------------------------------------------------------- |
| `actions`      | actions  | **Yes**  | The action(s) to execute. Uses standard HA automation syntax.                                      |
| `delay`        | duration | No\*     | How long to wait before running.                                                                   |
| `trigger_time` | datetime | No\*     | A specific date/time to run the action.                                                            |
| `name`         | string   | No       | A friendly name for the Logbook entry.                                                             |
| `id`           | string   | No       | A unique ID. If you schedule again with this ID, the old one is overwritten (resetting the timer). |
| `delay_from`   | datetime | No       | If using `delay`, calculate the delay starting from this specific timestamp instead of "now".      |

_\*Note: You must provide either `delay` or `trigger_time`._

#### Example: The "Robust" Turn Off

Turn off a light in 1 hour. If HA restarts in 30 minutes, the light will still turn off 30 minutes after boot.

```yaml
action: adhoc_scheduler.schedule
data:
  delay: "01:00:00"
  name: "Turn off Garage Light"
  actions:
    action: light.turn_off
    target:
      entity_id: light.garage
```

#### Example: Resettable Timer (Motion Light)

Every time this runs, it resets the timer to 5 minutes. If motion keeps happening, the light stays on.

```yaml
action: adhoc_scheduler.schedule
data:
  id: "kitchen_light_timer" # Re-using this ID overwrites the previous schedule
  delay:
    minutes: 5
  actions:
    action: light.turn_off
    target:
      entity_id: light.kitchen
```

#### Example: Schedule for a Specific Time

```yaml
action: adhoc_scheduler.schedule
data:
  trigger_time: "2025-12-25 07:00:00"
  name: "Christmas Morning Lights"
  actions:
    action: scene.turn_on
    target:
      entity_id: scene.christmas_morning
```

#### Example: Multiple Actions

Schedule multiple actions to run sequentially.

```yaml
action: adhoc_scheduler.schedule

data:
  delay:
    minutes: 10
  name: "Morning Routine Start"
  actions:
    - action: light.turn_on
      target:
        entity_id: light.bedroom_lamp
      data:
        brightness_pct: 50
    - action: media_player.volume_set
      target:
        entity_id: media_player.bedroom_speaker
      data:
        volume_level: 0.2
    - action: media_player.play_media
      target:
        entity_id: media_player.bedroom_speaker
      data:
        media_content_id: "spotify:playlist:YOUR_PLAYLIST_ID"
        media_content_type: "playlist"
```

### 2. `adhoc_scheduler.delete_schedule`

Cancels a pending schedule.

**Parameters:**

| Field | Type   | Required | Description                              |
| :---- | :----- | :------- | :--------------------------------------- |
| `id`  | string | **Yes**  | The unique ID of the schedule to cancel. |

#### Example: Cancel the Kitchen Timer

```yaml
action: adhoc_scheduler.delete_schedule
data:
  id: "kitchen_light_timer"
```

---

## 🤝 Contributing

Contributions are welcome! Please read the [Contribution guidelines](CONTRIBUTING.md).

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/Megabytemb/ha-adhoc-scheduler.svg?style=for-the-badge
[commits]: https://github.com/Megabytemb/ha-adhoc-scheduler/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/Megabytemb/ha-adhoc-scheduler.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/Megabytemb/ha-adhoc-scheduler.svg?style=for-the-badge
[releases]: https://github.com/Megabytemb/ha-adhoc-scheduler/releases
