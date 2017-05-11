# -*- coding: utf-8 -*-

from sys import getsizeof
from zeep import Client


class WorkflowEngineService:
    def __init__(self, url, user, password, company_id):
        self.url = url
        self.client = Client(self.url)
        self.user = user
        self.password = password
        self.company_id = company_id

    def get_card_data(self, data):
        """Transforma o dicionário em parâmetros."""
        if bool(data):
            # Obtém classes do webservice.
            kv_dto_array = self.client.get_type('ns1:keyValueDtoArray')
            kv_dto = self.client.get_type('ns1:keyValueDto')

            # Transforma o dicionário recebido nos objetos do webservice.
            fields = []
            for key, value in data.items():
                field = kv_dto(key=key, value=value)
                fields.append(field)
            parametros = kv_dto_array(item=fields)
            return parametros
        else:
            return {}

    def get_document_array(self, data):
        """Transforma o dicionário com informações dos anexos no tipo Document Array nativo do webservice ."""
        # Instanciamento dos tipos de dados.
        attachment_type = self.client.get_type('ns1:attachment')
        document_type = self.client.get_type('ns1:processAttachmentDto')
        documents_type = self.client.get_type('ns1:processAttachmentDtoArray')
        documents = []

        # Para todos os arquivos presentes na lista de arquivos.
        for file_name, file_info in data.items():
            # Informações do arquivo.
            file_content = file_info['content']
            file_description = file_info['description']

            # Criação do anexo.
            attachment = attachment_type(
                fileName=file_name,
                fileSize=getsizeof(file_content),
                filecontent=file_content,
            )

            # Criação do documento com o anexo.
            document = document_type(
                attachmentSequence=1,
                attachments=[attachment],
                companyId=1,
                deleted=False,
                description=file_description,
                isEdited=False,
                newAttach=True,
                processInstanceId=33061,
            )

            # Adiciona o documento à lista de documentos.
            documents.append(document)

        # Cria e retorna o array de documentos.
        document_array = documents_type(item=documents)
        return document_array

    def get_card_value(self, process_instance_id, user_id, card_field_name):
        """Retorna o valor de um campo da ficha.

        Args:
            process_instance_id (int): Número da solicitação.
            user_id (str): Matricula do colaborador.
            card_field_name(str): Nome do campo da ficha.

        Returns:
            str: Valor do campo.
        """
        result = self.client.service.getCardValue(self.user, self.password, self.company_id, process_instance_id,
                                                  user_id, card_field_name)
        return result

    def get_instance_card_data(self, process_instance_id, user_id):
        """Retorna o valor dos campos da ficha de uma solicitação.

        Args:
            process_instance_id(): .
            user_id(): .
        """
        result = self.client.service.getInstanceCardData(self.user, self.password, self.company_id, user_id,
                                                         process_instance_id)
        return result

    def save_and_send_task_classic(self, process_instance_id, choosed_state, colleague_ids, comments, user_id,
                                   card_data, manager_mode=False, thread_sequence=0, complete_task=True):
        """Movimenta solicitação para próxima atividade e retorna um array de objeto com chave e valor.
        
        Args:
            process_instance_id(): .
            choosed_state(): .
            colleague_ids(): .
            comments(): .
            user_id(): .
            card_data(): .
            manager_mode(): .
            thread_sequence(): .
            complete_task(): .
        """
        result = self.client.service.saveAndSendTaskClassic(self.user, self.password, self.company_id,
                                                            process_instance_id, choosed_state, colleague_ids, comments,
                                                            user_id, complete_task, attachments={},
                                                            cardData=self.get_card_data(card_data), appointment={},
                                                            managerMode=manager_mode, threadSequence=thread_sequence)
        return result

    def start_process_classic(self, process_id, user_id, colleague_ids, card_data, comments, attachments=None,
                              complete_task=True, choosed_state=0, manager_mode=False):
        """Inicia uma solicitação e retorna um array de objeto com chave e valor.

        Args:
            process_id(str): Código do processo.
            user_id(str): Matrícula do colaborador que vai iniciar a solicitação.
            colleague_ids(list): Colaborador que receberá a tarefa.
            card_data(dict): Dados da ficha dicionarizados.
            comments(str): Comentários.
            attachments(dict): Dicionário com nome e conteúdo lido dos arquivos anexos.
            complete_task(bool): Indica se deve completar a tarefa (True) ou somente salvar (False).
            choosed_state(int): Número da atividade.
            manager_mode(bool): Indica se colaborador esta iniciando a solicitação como gestor do processo.

        Returns:
            list: Lista com informações do objeto criado.
        """
        result = self.client.service.startProcessClassic(self.user, self.password, self.company_id, process_id,
                                                         choosed_state, colleague_ids, comments, user_id, complete_task,
                                                         attachments=self.get_document_array(attachments),
                                                         cardData=self.get_card_data(card_data), appointment={},
                                                         managerMode=manager_mode)
        return result
