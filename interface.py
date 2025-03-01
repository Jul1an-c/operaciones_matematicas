import flet as ft
import threading
from question_generator import generate_question
import voice_utils

# Estado de los switches
selected_tables_state = {i: False for i in range(1, 11)}

def create_switch_change_handler(i):
    def handler(e):
        selected_tables_state[i] = e.control.value
    return handler

# Vista de selección
class SelectionView(ft.View):
    def __init__(self):
        super().__init__(route="/")
        self.switch_controls = {}
        cards = []

        for i in range(1, 11):
            switch = ft.Switch(
                value=selected_tables_state[i],
                key=f"switch{i}",
                on_change=create_switch_change_handler(i),
                active_color=ft.Colors.GREEN
            )
            self.switch_controls[i] = switch
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(f"Tabla del {i}", size=20, color=ft.Colors.WHITE),
                        switch
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                padding=20,
                bgcolor=ft.Colors.BLACK87,
                border_radius=10,
                shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK54),
                width=150,
            )
            cards.append(card)

        switches_row = ft.Row(
            controls=cards,
            wrap=True,
            spacing=20,
            run_spacing=20,
            alignment=ft.MainAxisAlignment.CENTER
        )

        self.question_count_dropdown = ft.Dropdown(
            label="N° de preguntas",
            options=[
                ft.dropdown.Option("5"),
                ft.dropdown.Option("10"),
                ft.dropdown.Option("20"),
                ft.dropdown.Option("30")
            ],
            value="10",
            width=150,
            on_change=self.set_num_questions
        )
        self.num_questions = int(self.question_count_dropdown.value)

        new_quiz_button = ft.ElevatedButton(
            "Preguntar",
            icon=ft.Icons.PLAY_ARROW,
            width=150,
            on_click=self.new_quiz_click,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY_900, color=ft.Colors.WHITE)
        )
        button_card = ft.Container(
            content=new_quiz_button,
            alignment=ft.alignment.center,
            padding=20,
            border_radius=10,
            bgcolor=ft.Colors.BLACK87,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK54)
        )

        # Control de notificación
        self.notification_text = ft.Text("", size=16, color=ft.Colors.RED, text_align="center")

        self.controls.append(
            ft.Column(
                controls=[
                    ft.Text("Selecciona las tablas de multiplicar", size=30, weight="bold", text_align="center", color=ft.Colors.WHITE),
                    self.notification_text,
                    switches_row,
                    self.question_count_dropdown,
                    button_card
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=30,
                expand=True
            )
        )

    def set_num_questions(self, e):
        new_value = e.control.value
        try:
            self.num_questions = int(new_value)
        except (ValueError, TypeError):
            self.num_questions = 10
        self.question_count_dropdown.value = new_value
        self.update()

    def new_quiz_click(self, e):
        selected_tables = [i for i, v in selected_tables_state.items() if v]
        if not selected_tables:
            self.notification_text.value = "Selecciona al menos una tabla."
            self.update()
            return
        # Limpiar notificación
        self.notification_text.value = ""
        self.update()

        quiz_view = QuizView(selected_tables, self.num_questions)
        self.page.views.append(quiz_view)
        self.page.update()

# Vista del Quiz
class QuizView(ft.View):
    def __init__(self, selected_tables, num_questions=10):
        super().__init__(route="/quiz")
        self.selected_tables = selected_tables
        self.num_questions = num_questions
        self.questions = []
        self.current_index = 0
        self.score = 0
        self.incorrect_questions = []
        self.has_mic = voice_utils.has_microphone()

        # Indicador de carga de preguntas
        self.loading_text = ft.Text("Cargando preguntas...", size=24, color=ft.Colors.WHITE, text_align="center")

        # Interfaz completa de preguntas
        self.counter_text = ft.Text("", size=24, color=ft.Colors.WHITE, text_align="center")
        self.question_text = ft.Text("", size=80, weight="bold", color=ft.Colors.WHITE, text_align="center")
        self.question_container = ft.Container(
            content=self.question_text,
            padding=50,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.BLACK87,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK54),
            width=600,
            height=250
        )
        self.answer_field = ft.TextField(
            label="Tu respuesta (usa voz o escribe)",
            keyboard_type="number",
            width=300,
            disabled=False,
            border_color=ft.Colors.WHITE,
            text_style=ft.TextStyle(color=ft.Colors.WHITE),
            text_align="center"
        )
        self.submit_button = ft.ElevatedButton(
            "Enviar",
            icon=ft.Icons.SEND,
            width=120,
            on_click=self.check_answer,
            visible=False,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY_900, color=ft.Colors.WHITE)
        )
        self.next_button = ft.ElevatedButton(
            "Siguiente",
            icon=ft.Icons.SKIP_NEXT,
            width=120,
            on_click=self.next_question,
            visible=False,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY_900, color=ft.Colors.WHITE)
        )
        self.speak_button = ft.ElevatedButton(
            "Hablar",
            icon=ft.Icons.MIC,
            width=120,
            on_click=lambda e: threading.Thread(target=self.listen_for_voice, daemon=True).start(),
            visible=self.has_mic,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
        )
        self.cancel_button = ft.ElevatedButton(
            "Regresar",
            icon=ft.Icons.CANCEL,
            width=120,
            on_click=self.cancel_quiz,
            style=ft.ButtonStyle(bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
        )
        self.mic_status_text = ft.Text("", size=20, color=ft.Colors.YELLOW, text_align="center")
        self.feedback_text = ft.Text("", size=24, color=ft.Colors.WHITE, text_align="center")

        self.buttons_row = ft.Row(
            controls=[self.speak_button, self.submit_button, self.next_button, self.cancel_button],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )

        # Columna principal
        self.main_column = ft.Column(
            controls=[
                self.loading_text  # Mostramos el indicador de carga mientras se generan las preguntas
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
            expand=True
        )

        self.controls.append(ft.Container(content=self.main_column, alignment=ft.alignment.center, expand=True))

    def did_mount(self):
        # Generamos las preguntas
        threading.Thread(target=self.generate_questions, daemon=True).start()

    def generate_questions(self):
        self.questions = [generate_question(self.selected_tables) for _ in range(self.num_questions)]
        # Una vez generadas, actualizamos la interfaz para iniciar el quiz
        self.main_column.controls = [
            self.counter_text,
            self.question_container,
            self.answer_field,
            self.mic_status_text,
            self.buttons_row,
            self.feedback_text
        ]
        self.load_question()
        self.update()

    def load_question(self):
        current_q = self.questions[self.current_index]
        self.question_text.value = current_q["text"]
        self.answer_field.value = ""
        self.feedback_text.value = ""
        self.next_button.visible = False
        self.submit_button.visible = True
        self.speak_button.visible = self.has_mic
        self.counter_text.value = f"Pregunta {self.current_index + 1}/{self.num_questions}"
        self.question_container.bgcolor = ft.Colors.BLACK87
        self.update()
        threading.Thread(target=voice_utils.speak_text, args=(current_q["text"],), daemon=True).start()

    def listen_for_voice(self):
        self.mic_status_text.value = "Escuchando, hable ahora..."
        self.update()
        answer_text = voice_utils.listen_for_answer(timeout=10)
        if answer_text:
            self.answer_field.value = answer_text
            self.check_answer(None)
        else:
            self.feedback_text.value = "No se entendió la respuesta. Intenta de nuevo."
            self.feedback_text.color = ft.Colors.RED
            threading.Thread(target=voice_utils.speak_text, args=("No se entendió la respuesta. Intenta de nuevo.",), daemon=True).start()
            threading.Thread(target=voice_utils.speak_text, args=(self.questions[self.current_index]["text"],), daemon=True).start()
        self.mic_status_text.value = ""
        self.update()

    def check_answer(self, e):
        try:
            user_answer = int(self.answer_field.value)
        except ValueError:
            self.feedback_text.value = "La respuesta no es válida."
            self.feedback_text.color = ft.Colors.RED
            self.update()
            return

        current_q = self.questions[self.current_index]
        if user_answer == current_q["answer"]:
            self.question_container.bgcolor = ft.Colors.GREEN
            self.score += 1
            self.feedback_text.value = "¡Correcto!"
            self.feedback_text.color = ft.Colors.GREEN
            threading.Thread(target=voice_utils.speak_text, args=("¡Correcto!",), daemon=True).start()
        else:
            self.question_container.bgcolor = ft.Colors.RED
            self.incorrect_questions.append(current_q)
            self.feedback_text.value = f"Incorrecto. La respuesta es {current_q['answer']}."
            self.feedback_text.color = ft.Colors.RED
            threading.Thread(target=voice_utils.speak_text, args=(f"Incorrecto. La respuesta es {current_q['answer']}.",), daemon=True).start()

        self.submit_button.visible = False
        self.speak_button.visible = False
        self.next_button.visible = True
        self.update()

    def next_question(self, e):
        self.current_index += 1
        if self.current_index < self.num_questions:
            self.load_question()
        else:
            summary_view = QuizSummaryView(self.score, self.questions, self.incorrect_questions, self.selected_tables)
            self.page.views.clear()
            self.page.views.append(summary_view)
            self.page.update()

    def cancel_quiz(self, e):
        selection_view = SelectionView()
        self.page.views.clear()
        self.page.views.append(selection_view)
        self.page.update()

# Vista Resumen
class QuizSummaryView(ft.View):
    def __init__(self, score, questions, incorrect_questions, selected_tables):
        super().__init__(route="/summary")
        self.score = score
        self.questions = questions
        self.incorrect_questions = incorrect_questions
        self.selected_tables = selected_tables

        summary_text = ft.Text(
            value=f"¡Has completado el quiz!\nPuntuación: {score} / {len(questions)}",
            size=40,
            weight="bold",
            color=ft.Colors.WHITE,
            text_align="center"
        )

        incorrect_list = []
        for q in incorrect_questions:
            incorrect_list.append(
                ft.Text(
                    f"{q['text']} = {q['answer']}",
                    color=ft.Colors.RED,
                    size=24,
                    weight="bold"
                )
            )

        incorrect_column = ft.Column(
            controls=incorrect_list,
            visible=len(incorrect_list) > 0,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        back_button = ft.ElevatedButton(
            "Regresar",
            icon=ft.Icons.ARROW_BACK,
            width=150,
            on_click=self.go_back,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_GREY_900, color=ft.Colors.WHITE)
        )

        self.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[summary_text, incorrect_column, back_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=30
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        )

    def go_back(self, e):
        selection_view = SelectionView()
        self.page.views.clear()
        self.page.views.append(selection_view)
        self.page.update()

def main(page: ft.Page):
    page.title = "Repaso de Tablas de Multiplicar"
    page.bgcolor = ft.Colors.BLACK
    page.theme_mode = ft.ThemeMode.DARK

    selection_view = SelectionView()
    page.views.append(selection_view)
    page.update()

if __name__ == '__main__':
    ft.app(target=main)
