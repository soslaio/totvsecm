# -*- coding: utf-8 -*-

from sys import getsizeof
from zeep import Client


class WorkflowEngineService:
    def __init__(self, url, user, password, companyId):
        self.url = url
        self.client = Client(self.url)
        self.user = user
        self.password = password
        self.companyId = companyId

    def getCardData(self, data):
        """Transforma o dicionário em parâmetros."""
        keyValueDtoArray = self.client.get_type('ns1:keyValueDtoArray')
        keyValueDto = self.client.get_type('ns1:keyValueDto')
        fields = []
        for k, v in data.items():
            field = keyValueDto(key=k, value=v)
            fields.append(field)
        parametros = keyValueDtoArray(item=fields)
        return parametros

    def getDocumentArray(self, data):
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

    def getCardValue(self, processInstanceId, userId, cardFieldName):
        """Retorna o valor de um campo da ficha.

        Args:
            processInstanceId (int): Número da solicitação.
            userId (str): Matricula do colaborador.
            cardFieldName(str): Nome do campo da ficha.

        Returns:
            str: Valor do campo.
        """
        result = self.client.service.getCardValue(self.user, self.password, self.companyId, processInstanceId, userId,
                                                  cardFieldName)
        return result

    def getInstanceCardData(self, processInstanceId, userId):
        """Retorna o valor dos campos da ficha de uma solicitação."""
        result = self.client.service.getInstanceCardData(self.user, self.password, self.companyId, userId,
                                                         processInstanceId)
        return result

    def saveAndSendTaskClassic(self, processInstanceId, choosedState, colleagueIds, comments, userId, dcardData,
                               managerMode=False, threadSequence=0, completeTask=True):
        """Movimenta solicitação para próxima atividade e retorna um array de objeto com chave e valor."""
        result = self.client.service.saveAndSendTaskClassic(self.user, self.password, self.companyId, processInstanceId,
                                                            choosedState, colleagueIds, comments, userId, completeTask,
                                                            attachments={}, cardData=self.getCardData(dcardData),
                                                            appointment={}, managerMode=managerMode,
                                                            threadSequence=threadSequence)
        return result

    def startProcessClassic(self, processId, userId, colleagueIds, dcardData, attachments, comments, completeTask=True,
                            choosedState=0, managerMode=False):
        """Inicia uma solicitação e retorna um array de objeto com chave e valor.

        Args:
            processId (str): Código do processo.
            userId (str): Matrícula do colaborador que vai iniciar a solicitação.
            colleagueIds(list): Colaborador que receberá a tarefa.
            dcardData(dict): Dados da ficha dicionarizados.
            comments(str): Comentários.
            attachments(dict): Dicionário com nome e conteúdo lido dos arquivos anexos.
            completeTask(bool): Indica se deve completar a tarefa (True) ou somente salvar (False).
            choosedState(int): Número da atividade.
            managerMode(bool): Indica se colaborador esta iniciando a solicitação como gestor do processo.

        Returns:
            list: Lista com informações do objeto criado.
        """
        result = self.client.service.startProcessClassic(self.user, self.password, self.companyId, processId,
                                                         choosedState, colleagueIds, comments, userId, completeTask,
                                                         attachments=self.getDocumentArray(attachments),
                                                         cardData=self.getCardData(dcardData), appointment={},
                                                         managerMode=managerMode)
        return result
