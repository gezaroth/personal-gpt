import openai
# from keys import OPENAI_API_KEY
import time
import os
import json
from datetime import datetime
import requests
import logging
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)

model = "gpt-4o"


class AssistantManager:
    assistant_id = "asst_wrttLSKShCEg0myCiI9b8Mls"
    thread_id = ""

    def __init__(self, model: str = model):
        self.client = client
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None

        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(
                assistant_id=AssistantManager.assistant_id
            )
        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(
                thread_id=AssistantManager.thread_id
            )

    def create_assistant(self, name, instructions, tools):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(
                name=name, instructions=instructions, tools=tools, model=self.model
            )
            AssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"AssisID: {self.assistant.id}")

    def create_thread(self):
        if not self.thread:
            thread_obj = self.client.beta.threads.create()
            AssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"ThreadID: {self.thread.id}")

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id, role=role, content=content
            )

    def run_assistant(self, instructions):
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions,
            )

    def process_message(self):
        if self.thread:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
            summary = []

            last_message = messages.data[0]
            role = last_message.role
            response = last_message.content[0].text.value
            summary.append(response)

            self.summary = "\n".join(summary)
            print(f"SUMMARY-------> {role.capitalize()}: ====> {response}")

    # FOR STREAMLIT (FRONT END)
    def get_summary(self):
        return self.summary

    def wait_for_completion(self):
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id, run_id=self.run.id
                )
                print(f"RUN STATUS: {run_status.model_dump_json(indent=4)}")

                if run_status.status == "completed":
                    self.process_message()
                    break
                elif run_status.status == "requires_action":
                    print("FUNCTION CALLING NOW...")


    # RUN THE STEPS
    def run_steps(self):
        run_steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread.id, run_id=self.run.id
        )
        print(f"Run-Steps: {run_steps}")
        return run_steps.data



# if 'messages' not in st.session_state:
#     st.session_state['messages'] = []

# def main():
#     manager = AssistantManager()

#     st.title("Personal GPT")

#     with st.form(key="user_input_form"):
#         instructions = st.text_input("Enter topic")
#         submit_button = st.form_submit_button(label="Run Assistant")

#         if submit_button:
#             # Initialize and run the assistant
#             manager.create_assistant(
#                 name="Personal GPT",
#                 instructions=instructions,
#                 tools=[{"type": "code_interpreter"}]
#             )
#             manager.create_thread()

#             manager.add_message_to_thread(
#                 role="user",
#                 content=f"{instructions}?"
#             )
#             manager.run_assistant(instructions="Help me with the code")

#             # Wait for the completion of the assistant run
#             manager.wait_for_completion()

#             # Get the assistant's response
#             summary = manager.get_summary()

#             # Add the assistant's response to the messages session state
#             st.session_state["messages"].append({"role": "assistant", "content": summary})

#     # Display chat history from the session state
#     for message in st.session_state["messages"]:
#         with st.chat_message(message["role"]):
#             st.write(message["content"])

#     # Additional chat input for further interaction
#     if prompt := st.chat_input("What else can I help with?"):
#         # Append user input to session state and display it
#         st.session_state["messages"].append({"role": "user", "content": prompt})

#         with st.chat_message("user"):
#             st.write(prompt)

#         # Re-run the assistant with the new user input
#         manager.add_message_to_thread(
#             role="user",
#             content=prompt
#         )

#         manager.run_assistant(instructions="Process the latest message")
#         manager.wait_for_completion()

#         # Get the updated summary
#         summary = manager.get_summary()

#         with st.chat_message("assistant"):
#             st.markdown(summary)

#         # Optionally display additional information or logs
#         st.text("Run steps: ")
#         st.code(manager.run_steps(), line_numbers=True)

def main():
    manager = AssistantManager()

    st.title("Personal GPT")

    # Agregar un mensaje de inicio en el chat para simular "What can I help you with?"
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help with?"}]


    # Ingresar el tema o pregunta del usuario
    # with st.form(key="user_input_form"):
        # instructions = st.text_input("What can I help you with?")
        # submit_button = st.form_submit_button(label="Run Assistant")

        # if submit_button:
        #     # Inicializar y ejecutar el asistente con la entrada del usuario
        #     manager.create_assistant(
        #         name="Personal GPT",
        #         instructions=instructions,
        #         tools=[{"type": "code_interpreter"}]
        #     )
        #     manager.create_thread()

        #     # Agregar el mensaje del usuario a la conversación
        #     manager.add_message_to_thread(
        #         role="user",
        #         content=f"{instructions}?"
        #     )
        #     manager.run_assistant(instructions="Help me with the code")

        #     # Esperar la finalización del asistente
        #     manager.wait_for_completion()

        #     # Obtener la respuesta del asistente
        #     summary = manager.get_summary()

        #     # Agregar la respuesta del asistente a la sesión
        #     st.session_state["messages"].append({"role": "assistant", "content": summary})

    # Mostrar chat histórico de la sesión
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Entrada adicional para interactuar más
    if prompt := st.chat_input("Chat with personal GPT"):
        # Agregar el input del usuario a la sesión y mostrarlo
        st.session_state["messages"].append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)
        
        manager.create_thread()

        # Reejecutar el asistente con el nuevo input del usuario
        manager.add_message_to_thread(
            role="user",
            content=prompt
        )

        manager.run_assistant(instructions="Process the latest message")
        manager.wait_for_completion()

        # Obtener el resumen actualizado
        summary = manager.get_summary()

        with st.chat_message("assistant"):
            st.markdown(summary)

        st.session_state["messages"].append({"role": "assistant", "content": summary})

        # Opcional: Mostrar información adicional o logs
        st.text("Run steps: ")
        st.code(manager.run_steps(), line_numbers=True)

if __name__ == "__main__":
    main()
