
from sys import getsizeof
from zeep import Client


class WorkflowEngineService:
    def __init__(self, server, user, password, company_id, user_id, process_id=None):
        self.url = 'http://%s/webdesk/WorkflowEngineService?wsdl' % server
        self.client = Client(self.url)
        self.user = user
        self.password = password
        self.company_id = company_id
        self.user_id = user_id
        self.process_id = process_id

    def __get_card_data(self, data):
        """Transforma o dicionário em parâmetros."""
        if bool(data):
            # Obtém classes do webservice.
            try:
                kv_dto_array = self.client.get_type('ns0:keyValueDtoArray')
                kv_dto = self.client.get_type('ns0:keyValueDto')
            except:
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

    def __get_document_array(self, data):
        """Transforma o dicionário com informações dos anexos no tipo Document Array nativo do webservice ."""
        # Instanciamento dos tipos de dados.
        try:
            attachment_type = self.client.get_type('ns0:attachment')
            document_type = self.client.get_type('ns0:processAttachmentDto')
            documents_type = self.client.get_type('ns0:processAttachmentDtoArray')
        except:
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
                processInstanceId=1,
                fileName=file_name
            )

            # Adiciona o documento à lista de documentos.
            documents.append(document)

        # Cria e retorna o array de documentos.
        document_array = documents_type(item=documents)
        return document_array

    def calculate_deadline_hours(self, data, segundos, prazo, period_id):
        """Calcula um prazo a partir de uma data com base no expediente 
        e feriados cadastrados no produto passando o prazo em horas.

         Args:
            data(str): Data no formato yyy-MM-dd.
            segundos(int): Quantidade de segundos após a meia noite.
            prazo(int): Prazo que será aplicado em horas.
            period_id(str): Código de Expediente.

        Returns:
            str: Objeto DeadLineDto que contem variáveis com a data e hora.
        """
        result = self.client.service.calculateDeadLineHours(self.user, self.password, self.company_id, self.user_id,
                                                            data, segundos, prazo, period_id)
        return result

    def cancel_instance(self, process_instance_id, cancel_text):
        """Cancela uma solicitação.

         Args:
            process_instance_id(int): Número da solicitação.
            cancel_text(str): Comentários do cancelamento.

        Returns:
            str: Mensagem de retorno do cancelamento.
        """
        result = self.client.service.cancelInstance(self.user, self.password, self.company_id, process_instance_id,
                                                    self.user_id, cancel_text)
        return result

    def get_all_active_states(self, process_instance_id):
        """Retorna o número da atividade em que uma solicitação esta.

        Args:
            process_instance_id(int): Número da solicitação.

        Returns:
            list: Número da atividade.
        """
        result = self.client.service.getAllActiveStates(self.user, self.password, self.company_id, self.user_id,
                                                        process_instance_id)
        return result

    def get_attachments(self, process_instance_id):
        """Retorna os anexos de uma solicitação.
        
        Args:
            process_instance_id(int): Número da solicitação.

        Returns:
            list: Lista de anexos.
        """
        result = self.client.service.getAttachments(self.user, self.password, self.company_id, self.user_id,
                                                    process_instance_id)
        return result

    def get_card_value(self, process_instance_id, card_field_name):
        """Retorna o valor de um campo da ficha.

        Args:
            process_instance_id (int): Número da solicitação.
            card_field_name(str): Nome do campo da ficha.

        Returns:
            str: Valor do campo.
        """
        result = self.client.service.getCardValue(self.user, self.password, self.company_id, process_instance_id,
                                                  self.user_id, card_field_name)
        return result

    def get_histories(self, process_instance_id):
        """Retorna lista de históricos de um processo.

        Args:
            process_instance_id(int): Número da solicitação.

        Returns:
            list: Lista com as informações do formulário.
        """
        result = self.client.service.getHistories(self.user, self.password, self.company_id, self.user_id,
                                                  process_instance_id)
        return result

    def get_instance_card_data(self, process_instance_id):
        """Retorna o valor dos campos da ficha de uma solicitação.

        Args:
            process_instance_id(int): Número da solicitação.

        Returns:
            list: Lista com as informações do formulário.
        """
        result = self.client.service.getInstanceCardData(self.user, self.password, self.company_id, self.user_id,
                                                         process_instance_id)
        return result

    def save_and_send_task_classic(self, process_instance_id, choosed_state, colleague_ids, comments, card_data,
                                   manager_mode=False, thread_sequence=0, complete_task=True):
        """Movimenta solicitação para próxima atividade e retorna um array de objeto com chave e valor.

        Args:
            process_instance_id(int): Número da solicitação.
            choosed_state(int): Número da atividade.
            colleague_ids(list): Colaborador que receberá a tarefa.
            comments(unicode): Comentários.
            card_data(dict): Dados da ficha.
            manager_mode(bool): Indica se colaborador esta executando a tarefa como gestor do processo.
            thread_sequence(int): Indica se existe atividade paralela no processo. Se não existir o valor é 0 (zero),
                caso exista, este valor pode ser de 1 a infinito dependendo da quantidade de atividade paralelas
                existentes no processo.
            complete_task(bool): Indica se deve completar a tarefa (true) ou somente salvar (false).

        Returns:
            list: Lista com informações do objeto movimentado.
        """
        result = self.client.service.saveAndSendTaskClassic(self.user, self.password, self.company_id,
                                                            process_instance_id, choosed_state, colleague_ids, comments,
                                                            self.user_id, complete_task, attachments={},
                                                            cardData=self.__get_card_data(card_data), appointment={},
                                                            managerMode=manager_mode, threadSequence=thread_sequence)
        return result

    def start_process_classic(self, process_id, colleague_ids, card_data, comments, attachments=None,
                              complete_task=True, choosed_state=0, manager_mode=False):
        """Inicia uma solicitação e retorna um array de objeto com chave e valor.

        Args:
            process_id(str): Código do processo.
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
                                                         choosed_state, colleague_ids, comments, self.user_id,
                                                         complete_task, appointment={},
                                                         attachments=self.__get_document_array(attachments),
                                                         cardData=self.__get_card_data(card_data),
                                                         managerMode=manager_mode)
        return result
