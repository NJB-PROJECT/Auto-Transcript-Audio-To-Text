import flet as ft
import threading
import time
from recorder import AudioRecorder
from transcriber import Transcriber
from utils import save_to_txt, save_to_docx

def main(page: ft.Page):
    page.title = "Audio to Text - Realtime & Offline"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1000
    page.window.height = 700

    # --- Backend Initialization ---
    recorder = AudioRecorder()
    transcriber = Transcriber(model_size="small") # Use 'small' model

    # Check audio availability
    audio_status_msg = "Sistem Audio Siap (Zoom)" if recorder.is_system_audio_available else "PERINGATAN: Fitur rekam Zoom non-aktif (Hanya Mic)."
    audio_status_color = ft.Colors.GREEN if recorder.is_system_audio_available else ft.Colors.ORANGE
    start_btn_text = "Mulai Rekam (System Audio)" if recorder.is_system_audio_available else "Mulai Rekam (Microphone Only)"

    # State Variables
    is_recording = False
    stop_event = threading.Event()

    # UI Elements for Realtime Tab
    transcript_result = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def process_audio_queue():
        """Loop to process audio from queue and update UI."""
        while not stop_event.is_set():
            audio_chunk = recorder.get_audio()
            if audio_chunk is not None:
                text = transcriber.transcribe_segment(audio_chunk)
                if text.strip():
                    # Add to UI
                    transcript_result.controls.append(
                        ft.Container(
                            content=ft.Text(f"• {text}", size=16),
                            padding=5,
                            bgcolor=ft.Colors.GREY_100,
                            border_radius=5,
                            margin=2
                        )
                    )
                    page.update()
            time.sleep(0.1)

    def start_recording(e):
        nonlocal is_recording
        if is_recording: return

        is_recording = True
        stop_event.clear()

        btn_start.disabled = True
        btn_stop.disabled = False
        page.update()

        transcript_result.controls.append(ft.Text(f"Mulai merekam... ({start_btn_text})", color="green", italic=True))
        page.update()

        # Start Recorder
        recorder.start()

        # Start Processing Thread
        threading.Thread(target=process_audio_queue, daemon=True).start()

    def stop_recording(e):
        nonlocal is_recording
        if not is_recording: return

        is_recording = False
        stop_event.set()

        recorder.stop()

        btn_start.disabled = False
        btn_stop.disabled = True
        page.update()

        transcript_result.controls.append(ft.Text("Rekaman berhenti.", color="red", italic=True))
        page.update()

    def export_txt(e):
        filename = save_to_txt(transcript_result.controls)
        page.snack_bar = ft.SnackBar(ft.Text(f"Disimpan ke {filename}"))
        page.snack_bar.open = True
        page.update()

    def export_docx(e):
        filename = save_to_docx(transcript_result.controls)
        page.snack_bar = ft.SnackBar(ft.Text(f"Disimpan ke {filename}"))
        page.snack_bar.open = True
        page.update()

    btn_start = ft.ElevatedButton(start_btn_text, on_click=start_recording, icon=ft.Icons.MIC)
    btn_stop = ft.ElevatedButton("Stop", on_click=stop_recording, icon=ft.Icons.STOP, disabled=True, color="red")

    status_indicator = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.INFO, color=audio_status_color),
            ft.Text(audio_status_msg, color=audio_status_color, weight="bold")
        ]),
        padding=10,
        bgcolor=ft.Colors.GREY_50,
        border_radius=5
    )

    btn_export_txt = ft.ElevatedButton("Export TXT", icon=ft.Icons.SAVE, on_click=export_txt)
    btn_export_docx = ft.ElevatedButton("Export Word", icon=ft.Icons.DESCRIPTION, on_click=export_docx)

    # UI Elements for Upload Tab
    upload_result = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            upload_result.controls.append(ft.Text(f"File dipilih: {file_path}", weight="bold"))
            upload_result.controls.append(ft.Text("Sedang memproses... (Mohon tunggu)", color="blue"))
            page.update()

            def process_file():
                results = transcriber.transcribe_file(file_path)
                for line in results:
                    upload_result.controls.append(ft.Text(line))
                upload_result.controls.append(ft.Text("Selesai.", color="green", weight="bold"))
                page.update()

            threading.Thread(target=process_file, daemon=True).start()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    btn_upload = ft.ElevatedButton("Pilih File (MP4/MP3)", icon=ft.Icons.UPLOAD,
                                   on_click=lambda _: file_picker.pick_files(allow_multiple=False))

    # Navigation Logic
    def change_tab(e):
        idx = e.control.selected_index
        if idx == 0:
            content_area.content = realtime_view
        else:
            content_area.content = upload_view
        page.update()

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.MIC_EXTERNAL_ON, selected_icon=ft.Icons.MIC, label="Real-time"
            ),
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.Icons.CLOUD_UPLOAD), selected_icon_content=ft.Icon(ft.Icons.CLOUD_UPLOAD), label="Upload File"
            ),
        ],
        on_change=change_tab,
    )

    # Views
    realtime_view = ft.Container(
        content=ft.Column([
            status_indicator,
            ft.Row([btn_start, btn_stop, ft.VerticalDivider(), btn_export_txt, btn_export_docx]),
            ft.Divider(),
            ft.Container(
                content=transcript_result,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                padding=10,
                expand=True,
            )
        ]),
        padding=20,
        expand=True
    )

    upload_view = ft.Container(
        content=ft.Column([
            btn_upload,
            ft.Divider(),
            ft.Container(
                content=upload_result,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                padding=10,
                expand=True,
            )
        ]),
        padding=20,
        expand=True
    )

    content_area = ft.Container(content=realtime_view, expand=True)

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1),
                content_area,
            ],
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
