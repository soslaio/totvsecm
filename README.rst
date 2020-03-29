========================
totvsecm
========================

API para acesso aos Webservices do TOTVS ECM.

Highlights:
 * Compatível com Python 2.7, 3.5, 3.6, 3.7.
 * Compatível com TBC e SBC.


Instalação
------------

.. code-block:: bash

    pip install totvsecm

Uso
------------
.. code-block:: python

    from totvsecm import BaseService

    servico = BaseService(
        url_servidor='https://jedi_tbc_server',
        username_tbc='quigonjinn',
        senha_tbc='maytheforcebewithyou',
        username_ecm='quigonjinn',
        id_processo='selecao_jedi'
    )

Para iniciar um processo use:

.. code-block:: python

    servico.iniciar(
        dados_formulario=dict(nome='Anakin', sobrenome='Skywalker'),
        comentarios='Essa é a criança da profecia',
        ids_destinatarios=['yoda']
    )
