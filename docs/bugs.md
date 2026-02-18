# Bugs

> **📅 Last Updated:** February 11, 2026  
> **Document Version:** 1.0  
> **Status:** ✅ All bugs fixed (see bug-fixes-summary.md)

1. While transfering, I can't use the explorer.
   - It crashes or it stays on the loading circle.
   - What I want:
     - While transfering, I should be able to use the explorers within the application as the same time. (multi-tasking? multi-thread?)

2. When dragging a media file from Finder to the local explorer, inside a specfic directory, of the app, it copies the file and the logs says this:

   ```
   [14:33:45] ℹ️ Monitor: Tracking file stability: Love.Is.Blind.S10E03.1080p.HEVC.x265-MeGusta[EZTVx.to].mkv
   [14:33:45] ℹ️ Monitor: Waiting for stability: Love.Is.Blind.S10E03.1080p.HEVC.x265-MeGusta[EZTVx.to].mkv (0.0/2.0s)
   [14:33:45] ℹ️ Monitor: File still growing: Love.Is.Blind.S10E03.1080p.HEVC.x265-MeGusta[EZTVx.to].mkv (0 -> 13631488 bytes)
   [14:33:46] ℹ️ Monitor: File still growing: Love.Is.Blind.S10E03.1080p.HEVC.x265-MeGusta[EZTVx.to].mkv (13631488 -> 765887961 bytes)
   ```

   - The log pauses here and when I check the Finder, the file is completely copied into `~/Transfers/TV_shows/love_is_blind/Love.Is.Blind.mkv` but it doesn't begin transfering.
   - There is a copied file in `~/Transfers/TV_shows/love_is_blind/Love.Is.Blind.mkv`. I feel like it should not copy the file but completely move it because I don't want copies of media files.
   - What I want:
     - Don't copy the file
     - Dragging a file (folder or media) from Finder to local explorer should start the transfer after monitor stability.

3. Upload All button doesn't log activities as the program is going real-time.
   - Steps I did:
     - Clicked "Stop Monitoring"
     - Moved files within my Finder only.
     - Added media into a directory.
     - When I clicked "Upload All", the activity log did not update the steps one by one.
     - It felt like it crashed because the logs didn't update and my cursor was spinning for a long time.
   - Here is the current log:

   ```bash
    [14:54:00] ▶️ Monitor: Started watching: /Users/locle/Transfers
    [14:55:08] 🔍 Scanning for existing files...
    [14:55:08] ▶️ Auto Sync: Scanning for existing files...
    [14:55:08] ▶️ Scan: Start: /Users/locle/Transfers
    [14:55:08] ℹ️ Scan: Processing Movies directory
    [14:55:08] ℹ️ Scan: Processing TV_shows directory
    [14:55:08] ℹ️ Scan: TV show: andor
    [14:55:08] ℹ️ TV: Mapping /Users/locle/Transfers/TV_shows/andor -> /mnt/external/TV_shows/andor
    [14:55:08] ℹ️ Scan: TV show: dark_matter_2024
    [14:55:08] ℹ️ TV: Mapping /Users/locle/Transfers/TV_shows/dark_matter_2024 -> /mnt/external/TV_shows/dark_matter_2024
    [14:55:08] ℹ️ Scan: TV show: hells_kitchen_usa
    [14:55:08] ℹ️ TV: Mapping /Users/locle/Transfers/TV_shows/hells_kitchen_usa -> /mnt/external/TV_shows/hells_kitchen_usa
    [14:55:08] ℹ️ Scan: TV show: his_and_hers_2026
    [14:55:08] ℹ️ TV: Mapping /Users/locle/Transfers/TV_shows/his_and_hers_2026 -> /mnt/external/TV_shows/his_and_hers_2026
    [14:55:08] ℹ️ Scan: TV show: invasion_2021
    [14:55:08] ℹ️ TV: Mapping /Users/locle/Transfers/TV_shows/invasion_2021 -> /mnt/external/TV_shows/invasion_2021
    [14:55:08] ℹ️ Scan: TV show: love_is_blind
    [14:55:08] ℹ️ TV: Mapping /Users/locle/Transfers/TV_shows/love_is_blind -> /mnt/external/TV_shows/love_is_blind
    [14:55:08] ⬆️ Transfer: Start: File: /Users/locle/Transfers/TV_shows/love_is_blind/Love.Is.Blind.S10E05.1080p.HEVC.x265-MeGusta[EZTVx.to].mkv
    [14:56:25] ℹ️ Transfer: Verified: Love.Is.Blind.S10E05.1080p.HEVC.x265-MeGusta[EZTVx.to].mkv (759650713 bytes)
    [14:56:25] ✅ Transfer: Uploaded: File: /Users/locle/Transfers/TV_shows/love_is_blind/Love.Is.Blind.S10E05.1080p.HEVC.x265-MeGusta[EZTVx.to].mkv
    [14:56:25] 🗑️ Transfer: Completed: /Users/locle/Transfers/TV_shows/love_is_blind/Love.Is.Blind.S10E05.1080p.HEVC.x265-MeGusta[EZTVx.to].mkv
    [14:56:25] ℹ️ Scan: TV show: mf_ghost
    [14:56:25] ℹ️ TV: Mapping /Users/locle/Transfers/TV_shows/mf_ghost -> /mnt/external/TV_shows/mf_ghost
    [14:56:25] ℹ️ Scan: TV show: monarch_legacy_of_monsters
    [14:56:25] ℹ️ TV: Mapping /Users/locle/Transfers/TV_shows/monarch_legacy_of_monsters -> /mnt/external/TV_shows/monarch_legacy_of_monsters
    [14:56:25] ℹ️ Scan: TV show: singles_inferno
    [14:56:25] ℹ️ TV: Mapping /Users/locle/Transfers/TV_shows/singles_inferno -> /mnt/external/TV_shows/singles_inferno
    [14:56:25] ℹ️ Scan: TV show: supernatural
    [14:56:25] ℹ️ TV: Mapping /Users/locle/Transfers/TV_shows/supernatural -> /mnt/external/TV_shows/supernatural
    [14:56:25] ✅ Scan: Complete: /Users/locle/Transfers
   ```

   - The timestamps of `[14:55:08]` doesn't show up real-time. It all appears in the activity log right before the next timestamp, `[14:56:25]`. There is a big gap from `[14:54:00] ▶️ Monitor: Started watching:` and `[14:56:25] ℹ️ Transfer: Verified:`

   - What I Want:
     - When I open the application, and click "Upload All", I expect it to:
       - Have a status somewhere, illustrating that the process of scanning/using upload all has started.
       - Scan `~/Transfer/`
       - Log a list of new files that will transfer
       - Begin transfer process for each file
       - When all done, have the status change to done
   - Logs should start showing every step
   - I should be able to use the explorers at the same time (multi-tasking? multi-thread?)

4. I don't know when the monitor tracking file stability is done or the progress.
   - When I drag a file on my Finder to any directories in `/Tranfers` (Finder wise, not using the explorer), it starts the monitor tracking file, but it stops after that, or feels like it stops. It should start the transfer after. Here is the log

   ```bash
   [09:31:47] ℹ️ Monitor: Tracking file stability: .DS_Store
   [09:31:53] ℹ️ Monitor: Tracking file stability: Love.Is.Blind.S10E07.1080p.HEVC.x265-MeGusta[EZTVx.to].mkv
   ```

   - Sugestion:
     - Maybe use the progress bar to illustrate that the monitoring is doing something.
