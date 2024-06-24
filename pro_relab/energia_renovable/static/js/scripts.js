/*!
 * Start Bootstrap - Grayscale v7.0.5 (https://startbootstrap.com/theme/grayscale)
 * Copyright 2013-2022 Start Bootstrap
 * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-grayscale/blob/master/LICENSE)
 */
//
// Scripts
// 
/*vericar si conecto a js*/
console.log('Conectado a script');

//alerta de error login
$(document).ready(function() {
    $('#login-form').submit(function(e) {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function(response) {
                if (response === 'error') {
                    console.log("error")
                        //Alerta por si el correo y contraseña estan mal
                    $('#alertContainer').html('<div class="alert alert-danger">Verifica tu correo o contraseña.</div>');
                } else if (response === 'success') {
                    console.log("login")
                    window.location.href = '/inicio_principal';
                }
            },
            error: function() {
                // Error en la solicitud AJAX
                $('#alertContainer').html('<div class="alert alert-danger">Error en la solicitud.</div>');
            }
        });
    });
});

//alerta danger
$(document).ready(function() {
    $('#registro-form').submit(function(event) {
        // Evita el envío del formulario predeterminado
        event.preventDefault();

        // Verifica si el formulario HTML es válido
        if (this.checkValidity()) {
            // Obtiene la respuesta del hCaptcha
            var response = hcaptcha.getResponse();

            // Verifica si se proporcionó una respuesta válida
            if (response && response.trim() !== '') {
                // Envía el formulario a través de AJAX
                $.ajax({
                    type: 'POST',
                    url: $(this).attr('action'),
                    data: $(this).serialize(),
                    success: function(response) {
                        if (response === 'success') {
                            // Éxito: muestra un mensaje de éxito
                            $('#alertContainer').html('<div class="alert alert-success">Se ha creado la cuenta de manera exitosa.</div>');
                        } else if (response === 'exist') {
                            // Los datos ya existen: muestra una alerta
                            $('#alertContainer').html('<div class="alert alert-danger">Los datos ya existen.</div>');
                        }
                    },
                    error: function() {
                        // Error en la solicitud AJAX
                        $('#alertContainer').html('<div class="alert alert-danger">Error en la solicitud.</div>');
                    }
                });
            } else {
                // Si no se proporcionó una respuesta válida, muestra un mensaje de error
                $('#capContainer').html('<div class="alert alert-danger mt-3">Por favor completa el hCaptcha.</div>');
                setTimeout(function() {
                    document.getElementById("capContainer").style.display = "none";
                }, 2000); // 2000 milisegundos (2 segundos)
            }
        } else {
            // Si el formulario no es válido, permite que el navegador muestre los mensajes de error HTML5
            this.reportValidity();
        }
    });
});


//modal del panel
$(document).ready(function() {
    $('#modal_panel').on('click', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#modalPanel').modal('show');
        });
    });
});

//modal del bateria
$(document).ready(function() {
    $('#modal_bateria').on('click', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#modalBateria').modal('show');
        });
    });
});

//modal del inversor
$(document).ready(function() {
    $('#modal_inversor').on('click', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#modalInversor').modal('show');
        });
    });
});

//modal del proyecto
$(document).ready(function() {
    $('#modal_proyecto').on('click', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#modalProyecto').modal('show');
        });
    });
});

//modal proyecto inversor
$(document).ready(function() {
    $('#project_inversor').on('click', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#projectInversor').modal('show');
        });
    });
});

//modal proyecto inversor card
$(document).ready(function() {
    $('#project_inversor_card').on('click', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#projectInversorCard').modal('show');
        });
    });
});

//modal proyecto arreglo
$(document).ready(function() {
    $('#project_arreglo').on('click', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#projectArreglo').modal('show');
        });
    });
});


//modal serie pararlelo arreglo
$(document).ready(function() {
    $('[id^="projectSerie_"]').on('click', function(event) {
        event.preventDefault();
        var modalId = $(this).attr('id').split("_")[1];
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#projectSerie' + modalId).modal('show');
        });
    });
});

//modal proyecto banco
$(document).ready(function() {
    $('#project_banco').on('click', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#projectBanco').modal('show');
        });
    });
});

//modal proyecto banco dod
$(document).ready(function() {
    $('#project_bancoDOD').on('click', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#projectBancoDOD').modal('show');
        });
    });
});

//modal proyecto carga
$(document).ready(function() {
    $('#project_carga').on('click', function(event) {
        event.preventDefault();
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#projectCarga').modal('show');
        });
    });
});

//modal escribit potencia carga del projecto
$(document).ready(function() {
    $('[id^="projectCarga_"]').on('click', function(event) {
        event.preventDefault();
        var modalId = $(this).attr('id').split("_")[1];
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#projectCarga' + modalId).modal('show');
        });
    });
});

//modal serie pararlelo banco
$(document).ready(function() {
    $('[id^="projectSerieBanco_"]').on('click', function(event) {
        event.preventDefault();
        var modalId = $(this).attr('id').split("_")[1];
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#projectSerieBanco' + modalId).modal('show');
        });
    });
});

//modal eliminar arreglo del projecto
$(document).ready(function() {
    $('[id^="delArr_"]').on('click', function(event) {
        event.preventDefault();
        var modalId = $(this).attr('id').split("_")[1];
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#delArr' + modalId).modal('show');
        });
    });
});

//modal eliminar banco del projecto
$(document).ready(function() {
    $('[id^="delBan_"]').on('click', function(event) {
        event.preventDefault();
        var modalId = $(this).attr('id').split("_")[1];
        var url = $(this).attr('href');
        $.get(url, function(data) {
            $('#modalContent').html(data);
            $('#delBan' + modalId).modal('show');
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var imgInversor = document.querySelector('.esquina-inversor');
    var imgBanco = document.querySelector('.esquina-banco a');
    var card = document.querySelector('.card-dimension');
    var line = document.getElementById('myLine');

    function updateLine() {
        var imgInversorRect = imgInversor.getBoundingClientRect();
        var imgBancoRect = imgBanco.getBoundingClientRect();
        var cardRect = card.getBoundingClientRect();

        var x1 = imgInversorRect.right - cardRect.left + card.scrollLeft;
        var y1 = imgInversorRect.top - cardRect.top + imgInversorRect.height / 2 + card.scrollTop;
        var x2 = imgBancoRect.left - cardRect.left + card.scrollLeft;
        var y2 = imgBancoRect.top - cardRect.top + card.scrollTop;

        var length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
        var angle = Math.atan2(y2 - y1, x2 - x1);

        // Aplica las transformaciones a la línea
        line.style.width = length + 'px';
        line.style.transform = 'rotate(' + angle + 'rad)';
        line.style.top = y1 + 'px';
        line.style.left = x1 + 'px';

        // Solicita la próxima animación
        requestAnimationFrame(updateLine);
    }

    // Inicia la animación después de que se haya cargado el contenido
    window.addEventListener('load', updateLine);
});


//copiar texto del codigo del arduino

function copiarTexto() {
    // Seleccionar el texto a copiar
    var texto = document.getElementById("codigoACopiar");

    // Crear un elemento de entrada de texto oculto
    var input = document.createElement("input");
    input.setAttribute("value", texto.textContent);

    // Añadir el elemento al DOM
    document.body.appendChild(input);

    // Seleccionar el texto del elemento de entrada
    input.select();

    // Copiar el texto al portapapeles
    document.execCommand("copy");

    // Eliminar el elemento de entrada de texto oculto
    document.body.removeChild(input);

    // Mostrar un mensaje de éxito (esto es opcional)
    alert("Codigo Arduino Copiado");
}


window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function() {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }

    };

    // Shrink the navbar 
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            offset: 74,
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function(responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

});