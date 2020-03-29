
import json
from datetime import timedelta

from WorkflowEngineService import WorkflowEngineService
from DocumentService import DocumentService
from CardService import CardService


class BaseService:
    def __init__(self, url_servidor, username_tbc, senha_tbc, username_ecm, id_processo=None, numero_solicitacao=None,
                 numero_ficha=None, id_empresa=1):
        """Inicia uma instância da classe básica de conexão com o webservice do TOTVS ECM.

        Args:
            url_servidor (int): URL do servidor TBC, incluindo o protocolo, o domínio e a porta, caso necessário.
            username_tbc(str): Username do usuário do TBC.
            senha_tbc(str): Senha do usuário do TBC.
            username_ecm(str): Username do usuário responsável no ECM.
            id_processo(str): Identificador do processo no ECM.
            numero_solicitacao(int): Número da solicitação no ECM.
            numero_ficha(str): Número da ficha relacionada à solicitação no ECM.
            id_empresa(str): Identificador da empresa no ECM.
        """
        self.id_processo = id_processo
        self.numero_solicitacao = numero_solicitacao
        self.numero_ficha = numero_ficha
        self.usuario = username_tbc

        # instâncias dos serviços
        self.__workflowservice = WorkflowEngineService(url_servidor, user=username_tbc, password=senha_tbc,
                                                       company_id=id_empresa, user_id=username_ecm)
        self.__documentservice = DocumentService(url_servidor, user=username_tbc, password=senha_tbc,
                                                 company_id=id_empresa, user_id=username_ecm)
        self.__cardservice = CardService(url_servidor, user=username_tbc, password=senha_tbc, company_id=id_empresa,
                                         user_id=username_ecm)

    @staticmethod
    def __analisar_retorno(data, pkey):
        """Analisa o retorno do ECM em busca de informações."""
        for d in data:
            if d['key'] == pkey:
                return d['value']
        return None

    @property
    def anexos(self):
        """Retorna os anexos do processo. Não inclui os conteúdos por uma questão de otimização."""
        assert self.numero_solicitacao is not None, 'Informe o número da solicitação cujos anexos deseja.'

        attachments = {}

        # Consulta a lista de documentos relacionados ao processo.
        attachments_info = self.__workflowservice.get_attachments(self.numero_solicitacao)
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

    @property
    def atividade_atual(self):
        """Retorna a atividade no qual o processo se encontra atualmente."""
        assert self.numero_solicitacao is not None, 'Informe o número do processo cuja atividade atual deseja.'
        rs = self.__workflowservice.get_all_active_states(self.numero_solicitacao)
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
        """Histórico da solicitação."""
        assert self.numero_solicitacao is not None, 'Informe o número do processo cujo histórico deseja.'
        rs = self.__workflowservice.get_histories(self.numero_solicitacao)
        return rs

    @property
    def historico_tratado(self):
        """Retorna o histórico da solicitação de forma tratada."""
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
    def responsavel_atual(self):
        """Id do responsável atual da solicitação."""
        return self.historico_tratado[0]['colleague_id']

    def atualizar_formulario(self, dados_formulario):
        """Atualiza o formulário da solicitação.

        Args:
            dados_formulario(dict): Dicionário com os dados a serem atualizados no formulário.

        Returns:
            dict: Resultado da atualização da solicitação.
        """
        assert self.numero_ficha is not None, 'Informe o número da ficha que deseja atualizar.'
        result = self.__cardservice.update_card_data(self.numero_ficha, dados_formulario)
        return result

    def avancar(self, n_atividade, colleague_ids=None, manager_mode=False, observacao=u'Avançado automaticamente'):
        """Avança o processo para uma determinada atividade.

        Args:
            n_atividade(int): Número da atividade para qual a solicitação deve ser avançada.
            colleague_ids(list): Lista de usuários que receberão a solicitação.
            manager_mode(bool): Indica se colaborador esta executando a tarefa como gestor do processo.
            observacao(unicode): Comentários da movimentação.

        Returns:
            dict: Resultado do avanço da solicitação.
        """
        user = colleague_ids if colleague_ids else self.usuario
        assert self.numero_solicitacao is not None, 'Informe o número da solicitação que deseja avançar.'
        result = self.__workflowservice.save_and_send_task_classic(self.numero_solicitacao, n_atividade, [user],
                                                                   observacao, {}, manager_mode=manager_mode)
        return result

    def calcular_prazo(self, data, segundos, prazo, period_id):
        """Calcula o prazo de uma atividade considerando um expediente.

        Args:
            data(str): Data no formato yyy-MM-dd.
            segundos(int): Quantidade de segundos após a meia noite.
            prazo(int): Prazo que será aplicado em horas.
            period_id(str): Código de expediente.

        Returns:
            dict: Resultado do cálculo de prazo.
        """
        prazo = self.__workflowservice.calculate_deadline_hours(data=data, segundos=segundos, prazo=prazo,
                                                                period_id=period_id)
        prazo_str = prazo.__str__().replace('\'', '"')
        prazo_dict = json.loads(prazo_str)
        return prazo_dict

    def cancelar_solicitacao(self, mensagem):
        """Cancela a solicitação.

        Args:
            mensagem(str): Mensagem de cancelamento para o histórico.

        Returns:
            dict: Resultado do cancelamento da solicitação.
        """
        assert self.numero_solicitacao is not None, 'Informe o número do processo que deseja cancelar.'
        result = self.__workflowservice.cancel_instance(self.numero_solicitacao, mensagem)
        return result

    def carregar_solicitacao(self):
        """Carrega as informações da solicitação no objeto do serviço, incluindo número da ficha e ID do processo.

        Returns:
            dict: Dados do formulário da solicitação.
        """
        assert self.numero_solicitacao is not None, 'Informe o número do processo que deseja carregar.'

        # Carrega o número da ficha, que é um dos anexos da solicitação.
        attachments_info = self.__workflowservice.get_attachments(self.numero_solicitacao)
        for attachment in attachments_info:
            attachment_sequence = int(attachment['attachmentSequence'])
            if attachment_sequence == 1:
                self.numero_ficha = int(attachment['documentId'])

        # Carrega as informações do formulário como atributos da solicitação.
        result = self.__workflowservice.get_instance_card_data(self.numero_solicitacao)
        for item in result:
            attribute = item['item'][0]
            value = item['item'][1]
            setattr(self, attribute, value)

            # Carrega o id_processo. Poderia ser feito de outra forma
            # mais elegante, mas assim os editores não apontam erro.
            if attribute == 'WKDef':
                self.id_processo = value

        return result

    def filtrar_historico(self, sequencia, excluir_automaticos=True):
        """Filtra o histórico da solicitação a partir dos identificadores das sequências.

        sequencia(list): Lista de sequências a serem filtradas do histórico.
        excluir_automaticos(bool): Indica se as movimentações automáticas devem ser excluídas do histórico.

        Returns:
            list: Resultado do filtro do histórico.
        """
        rs = [h for h in self.historico_tratado if h['proxima_atividade'] in sequencia]

        # Aplica o filtro caso seja necessário excluir os históricos automáticos.
        if excluir_automaticos:
            rs = [h for h in rs if not h['colleague_id'].startswith('Pool')]

        return rs

    def iniciar_solicitacao(self, dados_formulario, ids_destinatarios, comentarios, anexos=None, completar=True,
                            numero_atividade=0, gestor_processo=False):
        """Inicia uma solicitação no ECM.

        Args:
            dados_formulario(dict): Número da solicitação.
            ids_destinatarios(list):
            comentarios(str): Comentário que fica registrado como
            anexos(dict): Dicionário com nome e conteúdo dos anexos.
            completar(bool): Indica se a tarefa deve ser completada ou apenas salva.
            numero_atividade(int): Número da atividade.
            gestor_processo(bool): Indica se a solicitação está sendo iniciada por um gestor do processo.

        Returns:
            dict: Resultado da inicialização da solicitação.
        """
        assert self.id_processo is not None, 'Informe o ID do processo que deseja iniciar.'
        result = self.__workflowservice.start_process_classic(process_id=self.id_processo,
                                                              colleague_ids=ids_destinatarios,
                                                              card_data=dados_formulario, comments=comentarios,
                                                              attachments=anexos, complete_task=completar,
                                                              choosed_state=numero_atividade,
                                                              manager_mode=gestor_processo)
        iprocess = self.__analisar_retorno(result, 'iProcess')
        if iprocess:
            self.numero_solicitacao = iprocess
            self.numero_ficha = self.__analisar_retorno(result, 'WDNrDocto')
            return result
        else:
            erro = self.__analisar_retorno(result, 'ERROR')
            raise Exception(erro)

    def movimentar(self, origem, destino, observacao='Movimentado automaticamente', **campos_atualizar):
        """Movimenta um processo de uma determinada atividade para outra, verificando antes a atividade de origem e
           possibilitando atualizar campos do formulário, caso necessário para o avanço.

        Args:
            origem(int): Número da atividade de origem, de onde a solicitação vai sair.
            destino(int): Número da atividade de destino, para onde a solicitação vai.
            observacao(str): Comentários da movimentação.
            campos_atualizar(dict): Dados a serem atualizados no formulário no momento da movimentação.

        Returns:
            dict: Resultado da movimentação da solicitação.
        """
        carddata = self.carregar_solicitacao()
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
