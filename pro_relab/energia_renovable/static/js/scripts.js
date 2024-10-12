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

//INICIO DE SESION
$(document).ready(function() {
    // Primero, eliminamos cualquier evento submit previo registrado
    $('#login-form').off('submit').on('submit', function(e) {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function(response) {
                if (response === 'error') {
                    console.log("error");
                    // Alerta por si el correo y contraseña están mal
                    $('#alertContainer').html('<div class="alert alert-danger">Verifica tu correo o contraseña.</div>');
                } else if (response === 'success') {
                    console.log("login");
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


//REGISTRO DE CUENTA
$(document).ready(function() {
    // Primero, eliminamos cualquier evento submit previo registrado
    $('#registro-form').off('submit').on('submit', function(event) {
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

// ----------------CREACION DE COMPONENTES ----------------
//modal del panel
$(document).ready(function() {
    $('#modal_panel').off('click').on('click', function(event) {
        event.preventDefault();
        // Abre el modal si no está ya visible
        if (!$('#modal_panel').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#modalPanel').modal('show');
            });
        }
    });
});

//modal del bateria
$(document).ready(function() {
    $('#modal_bateria').off('click').on('click', function(event) {
        event.preventDefault();
        // Abre el modal si no está ya visible
        if (!$('#modal_bateria').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#modalBateria').modal('show');
            });
        }
    });
});

//modal del inversor
$(document).ready(function() {
    $('#modal_inversor').off('click').on('click', function(event) {
        event.preventDefault();
        // Abre el modal si no está ya visible
        if (!$('#modal_inversor').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#modalInversor').modal('show');
            });
        }
    });
});

//modal del regulador
$(document).ready(function() {
    $('#modal_regulador').off('click').on('click', function(event) {
        event.preventDefault();
        // Abre el modal si no está ya visible
        if (!$('#modal_regulador').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#modalRegulador').modal('show');
            });
        }
    });
});

// ----------------CREACION DE PROYECTOS FOTOVOLTAICOS----------------
//modal del proyecto
$(document).ready(function() {
    $('.modal_proyecto').off('click').on('click', function(event) {
        event.preventDefault();
        
        // Abre el modal si no está ya visible
        if (!$('#modalProyecto').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#modalProyecto').modal('show');
            });
        }
    });
});

//modal proyecto inversor
$(document).ready(function() {
    $('.project_inversor').off('click').on('click', function(event) {
        event.preventDefault();
        // Abre el modal si no está ya visible
        if (!$('.project_inversor').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#projectInversor').modal('show');
            });
        }
    });
});

//modal proyecto regulador
$(document).ready(function() {
    $('#project_regulador').off('click').on('click', function(event) {
        event.preventDefault();
        // Abre el modal si no está ya visible
        if (!$('#project_regulador').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#projectRegulador').modal('show');
            });
        }
    });
});

//modal proyecto arreglo
$(document).ready(function() {
    $('#project_arreglo').off('click').on('click', function(event) {
        event.preventDefault();
        // Abre el modal si no está ya visible
        if (!$('#project_arreglo').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#projectArreglo').modal('show');
            });
        }
    });
});


//modal serie pararlelo arreglo
$(document).ready(function() {
    $('[id^="projectSerie_"]').off('click').on('click', function(event) {
        event.preventDefault();
        var modalId = $(this).attr('id').split("_")[1];
        // Abre el modal si no está ya visible
        if (!$('[id^="projectSerie_"]').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#projectSerie' + modalId).modal('show');
            });
        }
    });
});

//modal proyecto banco
$(document).ready(function() {
    $('#project_banco').off('click').on('click', function(event) {
        event.preventDefault();
        // Abre el modal si no está ya visible
        if (!$('#project_banco').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#projectBanco').modal('show');
            });
        }
    });
});

//modal proyecto banco dod
$(document).ready(function() {
    $('#project_bancoDOD').off('click').on('click', function(event) {
        event.preventDefault();
        // Abre el modal si no está ya visible
        if (!$('#project_bancoDOD').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#projectBancoDOD').modal('show');
            });
        }
    });
});

//modal proyecto carga
$(document).ready(function() {
    $('#project_carga').off('click').on('click', function(event) {
        event.preventDefault();
        // Abre el modal si no está ya visible
        if (!$('#project_carga').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#projectCarga').modal('show');
            });
        }
    });
});

//modal escribit potencia carga del projecto
$(document).ready(function() {
    $('[id^="projectCarga_"]').off('click').on('click', function(event) {
        event.preventDefault();
        var modalId = $(this).attr('id').split("_")[1];
        // Abre el modal si no está ya visible
        if (!$('[id^="projectCarga_"]').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#projectCarga' + modalId).modal('show');
            });
        }
    });
});

//modal serie pararlelo banco
$(document).ready(function() {
    $('[id^="projectSerieBanco_"]').off('click').on('click', function(event) {
        event.preventDefault();
        var modalId = $(this).attr('id').split("_")[1];
        // Abre el modal si no está ya visible
        if (!$('[id^="projectSerieBanco_"]').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);                
                $('#projectSerieBanco' + modalId).modal('show');
                console.log('#projectSerieBanco' + modalId);
            });
        }
    });
});

//modal eliminar arreglo del projecto
$(document).ready(function() {
    $('[id^="delArr_"]').off('click').on('click', function(event) {
        event.preventDefault();
        var modalId = $(this).attr('id').split("_")[1];
        // Abre el modal si no está ya visible
        if (!$('[id^="delArr_"]').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#delArr' + modalId).modal('show');
            });
        }
    });
});

//modal eliminar banco del projecto
$(document).ready(function() {
    $('[id^="delBan_"]').off('click').on('click', function(event) {
        event.preventDefault();
        var modalId = $(this).attr('id').split("_")[1];
        // Abre el modal si no está ya visible
        if (!$('[id^="delBan_"]').hasClass('show')) {
            $.get($(this).attr('href'), function(data) {
                $('#modalContent').html(data);
                $('#delBan' + modalId).modal('show');
            });
        }
    });
});

//TOOLTIP
document.addEventListener('DOMContentLoaded', function() {
    const exampleEl = document.getElementById('agregar-costo');
    const tooltip = new bootstrap.Tooltip(exampleEl);
}); 
document.addEventListener('DOMContentLoaded', function() {
    const tooltipElements = document.querySelectorAll('.tooltip_btn'); // Selecciona todos los elementos con la clase 'tooltip'
    
    tooltipElements.forEach(function(element) {
        new bootstrap.Tooltip(element); // Aplica Bootstrap Tooltip a cada elemento
    });
});
