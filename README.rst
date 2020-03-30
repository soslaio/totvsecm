========================
totvsecm
========================

API para acesso aos Webservices do TOTVS ECM.

Highlights:
 * Compatível com Python 2.7, 3.5, 3.6, 3.7.
 * Compatível com a versão 48-EP12 82 do ECM.

Instalação
------------
.. code-block:: bash

    pip install totvsecm

Uso
------------
.. code-block:: python

    from totvsecm import BaseService

    servico = BaseService(
        url_servidor='https://jedi_ecm_server',
        usuario='quigonjinn',
        senha='maytheforcebewithyou',
        usuario_responsavel='quigonjinn',
        id_processo='selecao_jedi'
    )

Para iniciar um processo use:

.. code-block:: python

    servico.iniciar_solicitacao(
        dados_formulario=dict(nome='Anakin', sobrenome='Skywalker'),
        ids_destinatarios=['yoda'],
        comentarios='He is the chosen one'
    )
