==========
AutoPython
==========

AutoPython se hace pasar por el shell de Python en el que en lugar de esperar el ingreso de sentencias, a éstas se las toma de un script normal de Python y se simula el ingreso de las mismas como si se las estuviera escribiendo por teclado, haciendo además resaltado de sintaxis con colores y permitiendo la navegación rápida entre las sentencias usando un número de índice asignado a cada una. Ideal para demostraciones o presentaciones en vivo con mucho código para mostrar. AutoPython está escrito para Python 3.


Instalación:
------------

Si tenés instalado pip_, alcanza con ejecutar:

.. code-block:: bash

        $ pip install autopython


Requerimientos:
---------------

AutoPython tiene como dependencias los siguientes módulos:

- Colorama_
- Pygments_


Como usar AutoPython:
---------------------

Simplemente ejecutándolo dándole como parámetro el nombre el archivo fuente que se quiere presentar.

.. code-block:: bash

        $ autopython tutorial.py


El script dado deberá contener cada una de las sentencias o fragmentos de código a mostrar y esta herramienta se encargará de simular durante una presentación el ingreso de cada una de esas sentencias, como si se las estuviera escribiendo directamente en el propio shell de Python.

Tras invocar a AutoPython con el nombre del script previamente preparado, se puede ver en la consola exactamente lo mismo que se vería en el shell de Python: Una leyenda con la versión del intérprete y demás información, seguido del prompt ``>>>`` que señala la espera del ingreso de la próxima sentencia a ejecutar.

A partir de este punto es donde esta herramienta difiere radicalmente del shell real. En lugar de permitir el ingreso libre de código, AutoPython espera que se presionen determinadas teclas para controlar lo que vaya a suceder a continuación.

Si se oprime la tecla de avance (que puede ser tanto ``Av.Pág`` como ``Espacio`` o ``Enter``) se procede a simular el ingreso por teclado de la primer sentencia contenida en el script dado. El ingreso de la sentencia se hará escribiendo en la consola de a un carácter a la vez, a una velocidad configurable pero variable de tipeo, insertando pausas aleatorias para darle más realismo a la simulación. Tras completar el ingreso de dicha sentencia, el cursor quedará al final de la última línea escrita, en el punto donde, si fuera ingresada en el shell real, sólo faltaría presionar ``Enter`` para ejecutarla.

Si a continuación se vuelve a oprimir nuevamente la tecla de avance, AutoPython finaliza el ingreso de la sentencia simulando presionar ``Enter`` y mostrando en la consola exactamente el mismo resultado que dicho código produciría si fuera ingresado en el shell de Python. Oprimiendo reiteradas veces la tecla de avance permite ir mostrando y ejecutando las sucesivas sentencias contenidas en el resto del script.

Vale la pena destacar que la ejecución de cada una de las sentencias no es simulada sino que se utiliza al propio intérprete de Python para dicho fin. Todo resultado que se observe será el mismo que se obtendría al ingresar la misma sentencia en el shell de Python.

AutoPython intenta imitar de la mejor manera posible la apariencia y el comportamiento del propio shell interactivo de Python. Se prestó gran atención en reproducir el comportamiento del shell real al ingresar una sentencia de varias líneas, donde el prompt alterna entre ``>>>`` y ``...`` según si se continúa o no con el ingreso de dicha sentencia.

Pero eso no es todo lo que la herramienta hace: El código fuente se presenta con colores empleando resaltado de sintaxis, una sentencia muy larga es cortada automáticamente en varias líneas para mostrarse completa y cada sentencia ejecutable es numerada con un índice (comenzando en 1) para poder hacerle referencia fácilmente, mostrando el número de sentencia entre paréntesis al final de la primera (y posiblemente, única) línea de código. En el caso que existan comentarios dentro del código fuente, éstos no serán considerados como sentencias ejecutables y simplemente se los escribirá sin pausas, deteniéndose recién al llegar a la próxima sentencia.

AutoPython permite volver hacia atrás, utilizando la tecla de retroceso (configurada como ``Re.Pág`` o la letra ``P``), regresando a sentencias que fueron mostradas anteriormente. Este comportamiento es análogo a volver a escribir una sentencia ya ingresada y no tiene ningún otro efecto en el estado interno del intérprete: Retroceder no deshace los efectos causados por una sentencia previamente ejecutada. Si se usa la tecla de retroceso en el punto en el que se está por ejecutar una sentencia (o sea, se oprimió una vez la tecla de avance, se mostró la sentencia pero aún no se la ejecutó), se simula el comportamiento de usar ``Control-C`` para cancelar dicha entrada y se procede a simular el ingreso de la sentencia anterior a ésta. Si, en cambio, se usa la tecla de retroceso luego de ejecutar una sentencia (es decir, se oprimió dos veces la tecla de avance), AutoPython vuelve a repetir el ingreso de la última sentencia ejecutada. Un efecto similar se consigue con la tecla de repetición (tecla ``R``) que repite el ingreso de la última sentencia mostrada, independientemente de si ésta se llegó a ejecutar.

La herramienta aprovecha el hecho de que todas las sentencias ejecutadas son numeradas con un índice y permite saltar directamente a una sentencia indicando su número, utilizando la tecla de salto (tecla ``G``). En este caso, el resultado observado varía de acuerdo a donde se encuentre la sentencia a saltar con respecto a la que se mostró por última vez: Si se desea saltar a una instrucción posterior, se procede a ejecutar una a una todas las sentencias necesarias para llegar desde donde está actualmente hasta la sentencia pedida. Dicha ejecución se realiza sin efectos de tipeo, para no producir pausas innecesarias. Si, en cambio, se pidió saltar a una sentencia anterior, se asume que se desea volver a escribir dicha sentencia en el contexto en que originalmente se previó su ejecución, por lo que se reinicia el estado interno del intérprete (como si recién hubiera arrancado) y se vuelven a ejecutar desde el principio todas y cada una de las sentencias necesarias para llegar a la sentencia indicada. El número de sentencia sigue la semántica de los índices en las secuencias de Python, donde valores positivos indican desplazamientos a partir del inicio mientras que valores negativos señalan desplazamientos desde el final de la secuencia. Así, el índice -1 indica que se quiere mostrar la ejecución de la última sentencia del script.

AutoPython provee la posibilidad de que en cualquier momento el orador decida tomar el control del intérprete y comenzar a introducir sentencias de la misma manera que lo haría en el propio shell de Python. Esto se logra presionando la tecla de shell (tecla ``S``). Cuando la herramienta entra en modo interactivo, toda sentencia que se escriba por teclado procederá a ejecutarse inmediatamente en el contexto del intérprete usado durante el ingreso automático de AutoPython, de forma que todo efecto que dichas sentencias produzcan afectará al resto de las sentencias que se ejecuten más tarde (ya sean ingresadas manualmente o en forma automática). El modo de simulación se abandona utilizando la combinación de teclas ``EOF`` (End Of File o fin de archivo) que sobre los sistemas operativos basados en Windows se indica con la combinación de teclas ``Control-Z`` mientras que en sistemas operativos derivados de Unix se utiliza la combinación ``Control-D``.

Finalmente, la tecla de salida (tecla ``Q``) permite terminar la ejecución de la herramienta en cualquier punto de la presentación, cancelando toda sentencia pendiente de ser ejecutada y mostrando la llamada a la función ``quit()``, que normalmente causa el cierre del intérprete.

Durante una presentación, AutoPython genera un archivo de bitácora en donde se almacena todo lo realizado: Inicio de la presentación, avance a la próxima sentencia, ejecución de la sentencia, retrocesos, repeticiones, saltos y cambios a modo interactivo junto con todas las sentencias ingresadas manualmente.
Toda esta información se guarda junto con una marca de tiempo indicando en qué momento se realizó cada acción. Esto se hace con la finalidad de poder analizar y depurar el script preparado, permitiendo detectar largas pausas entre sentencias, saltos aleatorios dentro de la secuencia prevista o sentencias ingresadas por el orador que probablemente deberían estar contenidas como parte de la exposición armada.

La velocidad de tipeo es configurable y se la indica como la demora mínima entre letra y letra, realizándose una demora al azar entre ese mínimo y el doble del mismo.

AutoPython es multiplataforma y debería funcionar tanto sobre Windows como Mac OS X o Linux (aunque mayormente se lo prueba sobre este último).


Cosas por hacer:
----------------

- Agregar parámetros para la línea de comandos que permitan configurar las opciones disponibles.
- Separar la lógica de la presentación, para poder simular/utilizar otros shells (consola de IPython, te estoy mirando...).
- Más temas de colores para el resaltado de sintaxis.
- English translation.
- ???
- Profit!


Licencia:
---------

Copyright Germán Osella Massa 2016. Licencia GPLv3. Ver archivo `LICENSE.txt`_.


.. _pip: http://www.pip-installer.org/
.. _Colorama: https://github.com/tartley/colorama
.. _Pygments: http://pygments.org/
.. _LICENSE.txt: https://github.com/gosella/autopython/blob/master/LICENSE.txt
