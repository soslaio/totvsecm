
import json
from datetime import timedelta

from WorkflowEngineService import WorkflowEngineService
from DocumentService import DocumentService
from CardService import CardService


class BaseService:
    def __init__(self, servidor, usuario, senha, id_responsavel, id_processo=None, id_empresa=1, numero_ecm=None,
                 ficha=None):
        self.id_processo = id_processo
        self.numero_ecm = numero_ecm
        self.ficha = ficha
        self.usuario = usuario

        # instâncias dos serviços
        self.__workflowservice = WorkflowEngineService(servidor, user=usuario, password=senha, company_id=id_empresa,
                                                       user_id=id_responsavel)
        self.__documentservice = DocumentService(servidor, user=usuario, password=senha, company_id=id_empresa,
                                                 user_id=id_responsavel)
        self.__cardservice = CardService(servidor, user=usuario, password=senha, company_id=id_empresa,
                                         user_id=id_responsavel)

    @staticmethod
    def __analisar_retorno(data, pkey):
        """Analisa o retorno do ECM em busca de informações."""
        for d in data:
            if d['key'] == pkey:
                return d['value']
        return None

    @property
    def atividade_atual(self):
        """Retorna a atividade no qual o processo se encontra atualmente."""
        assert self.numero_ecm is not None, 'Informe o número do processo cuja atividade atual deseja.'
        rs = self.__workflowservice.get_all_active_states(self.numero_ecm)
        if rs:
            return [int(n) for n in rs]
        else:
            return [-1]

    @property
    def finalizado(self):
        """Indica se o processo foi finalizado."""
        return self.atividade_atual == [-1]

    @property
    def historico(self):
        assert self.numero_ecm is not None, 'Informe o número do processo cujo histórico deseja.'
        rs = self.__workflowservice.get_histories(self.numero_ecm)
        return rs

    @property
    def responsavel_atual(self):
        return self.historico_tratado[0]['colleague_id']

    @property
    def historico_tratado(self):
        historico = self.historico
        rs = list()
        for etapa in historico:
            for task in etapa.tasks:
                data_hora = task.taskCompletionDate + timedelta(seconds=task.taskCompletionHour) \
                    if task.taskCompletionDate else None
                data_hora_formatada = data_hora.strftime('%d/%m/%Y %H:%M') if task.taskCompletionDate \
                    else u'Tarefa não finalizada'
                rs.append({
                    'data_hora': data_hora,
                    'data_hora_formatada': data_hora_formatada,
                    'proxima_atividade': int(task.choosedSequence),
                    'observacao': task.taskObservation,
                    'colleague_id': task.colleagueId,
                    'texto': task.historCompleteColleague,
                    'nome_responsavel': task.historCompleteColleague.split('\n')[0]
                })
        return rs

    @property
    def anexos(self):
        """Retorna os anexos do processo. Não inclui os conteúdos por uma questão de otimização."""
        assert self.numero_ecm is not None, 'Informe o número do processo cujos anexos deseja.'

        attachments = {}

        # Consulta a lista de documentos relacionados ao processo.
        attachments_info = self.__workflowservice.get_attachments(self.numero_ecm)
        for attachment in attachments_info:
            attachment_sequence = int(attachment['attachmentSequence'])

            # Exclui o primeiro anexo da lista, que é o formulário do processo.
            if attachment_sequence > 1:
                # Armazena as informações do documento.
                document_id = int(attachment['documentId'])
                colleague_id = attachment['colleagueId']

                # Consulta as informações do documento.
                document_info = self.__documentservice.get_active_document(document_id, colleague_id)[0]
                phisical_file = document_info['phisicalFile']
                version = int(document_info['version'])

                # Consulta o conteúdo do documento.
                # document_content = self.__documentservice.get_document_content(document_id, colleague_id, version,
                #                                                                phisical_file)

                # Adiciona o anexo ao dicionário de anexos.
                attachments[phisical_file] = {
                    'colleague_id': colleague_id,
                    'document_id': document_id,
                    'version': version,
                    # 'document_content': document_content,
                }
        return attachments

    def filtrar_historico(self, sequencia, excluir_automaticos=True):
        rs = [h for h in self.historico_tratado if h['proxima_atividade'] in sequencia]

        # Aplica o filtro caso seja necessário excluir os históricos automáticos.
        if excluir_automaticos:
            rs = [h for h in rs if not h['colleague_id'].startswith('Pool')]

        return rs

    def iniciar(self, dados_formulario, comentarios, anexos, ids_destinatarios, completar=True, numero_atividade=0,
                gestor_processo=False):
        """Inicia um processo."""
        assert self.id_processo is not None, 'Informe o ID do processo que deseja iniciar.'
        result = self.__workflowservice.start_process_classic(process_id=self.id_processo,
                                                              colleague_ids=ids_destinatarios,
                                                              card_data=dados_formulario, comments=comentarios,
                                                              attachments=anexos, complete_task=completar,
                                                              choosed_state=numero_atividade,
                                                              manager_mode=gestor_processo)
        iprocess = self.__analisar_retorno(result, 'iProcess')
        if iprocess:
            self.numero_ecm = iprocess
            self.ficha = self.__analisar_retorno(result, 'WDNrDocto')
            return result
        else:
            erro = self.__analisar_retorno(result, 'ERROR')
            raise Exception(erro)

    def carregar(self):
        """Carrega as informações do processo, incluindo número da ficha e ID do processo."""
        assert self.numero_ecm is not None, 'Informe o número do processo que deseja carregar.'

        # Carrega o número da ficha.
        attachments_info = self.__workflowservice.get_attachments(self.numero_ecm)
        for attachment in attachments_info:
            attachment_sequence = int(attachment['attachmentSequence'])
            if attachment_sequence == 1:
                self.ficha = int(attachment['documentId'])

        # Carrega as informações do formulário como atributos do processo.
        result = self.__workflowservice.get_instance_card_data(self.numero_ecm)
        for item in result:
            attribute = item['item'][0]
            value = item['item'][1]
            setattr(self, attribute, value)

            # Carrega o id_processo. Poderia ser feito de outra forma
            # mais elegante, mas assim os editores não apontam erro.
            if attribute == 'WKDef':
                self.id_processo = value

        return result

    def atualizar_formulario(self, dados_formulario):
        """Atualiza o formulário do processo."""
        assert self.ficha is not None, 'Informe o número da ficha que deseja atualizar.'
        result = self.__cardservice.update_card_data(self.ficha, dados_formulario)
        return result

    def cancelar(self, mensagem):
        """Cancela o processo."""
        assert self.numero_ecm is not None, 'Informe o número do processo que deseja cancelar.'
        result = self.__workflowservice.cancel_instance(self.numero_ecm, mensagem)
        return result

    def avancar(self, n_atividade, colleague_ids=None, manager_mode=False, observacao=u'Avançado automaticamente'):
        """Avança o processo para uma determinada atividade."""
        user = colleague_ids if colleague_ids else self.usuario
        assert self.numero_ecm is not None, 'Informe o número do processo que deseja avançar.'
        result = self.__workflowservice.save_and_send_task_classic(self.numero_ecm, n_atividade, [user],
                                                                   observacao, {}, manager_mode=manager_mode)
        return result

    def calcular_prazo(self, data, segundos, prazo, period_id):
        """Calcula o prazo de uma atividade considerando um expediente."""
        prazo = self.__workflowservice.calculate_deadline_hours(data=data, segundos=segundos, prazo=prazo,
                                                                period_id=period_id)
        prazo_str = prazo.__str__().replace('\'', '"')
        prazo_dict = json.loads(prazo_str)
        return prazo_dict

    def movimentar(self, origem, destino, observacao='Movimentado automaticamente', **campos_atualizar):
        """Movimenta um processo de uma determinada atividade para outra, verificando antes a atividade de origem
        e possibilitando atualizar campos do formulário, caso necessário para o avanço."""
        carddata = self.carregar()
        if not self.finalizado:
            if self.atividade_atual[0] == origem:
                # Caso haja campos para atualizar antes de avançar o processo.
                if campos_atualizar:
                    for campo, valor in campos_atualizar.items():
                        if hasattr(self, campo):
                            for obj in carddata:
                                item = obj['item']
                                nome = item[0]
                                if nome == campo:
                                    item[1] = valor
                        else:
                            raise Exception(f'O processo não possui o campo "{campo}".')
                    self.atualizar_formulario(carddata)
                return self.avancar(destino, observacao=observacao, manager_mode=True)
            else:
                raise Exception(f'O processo não está na atividade de origem esperada.')
        else:
            raise Exception('O processo já está finalizado.')
