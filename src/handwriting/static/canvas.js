window.onload = function new_fabric(){
  var canvas = new fabric.Canvas('sheet');
  canvas.isDrawingMode = true;
  canvas.freeDrawingBrush.width = 20;
  canvas.freeDrawingBrush.color = "#000000";
};

function send_image_data() {
  $('form input[name=image_data]').val(sheet.toDataURL("image/png"));
  $('form input[name=width]').val(sheet.width);
  $('form input[name=height]').val(sheet.height);
  // $('form input[name=digit]').val(document.getElementById("form_digit").value);
  // console.log('form was submitted');
  $('form').submit();
};

function clear_canvas() {
  var canvas = document.getElementById('sheet');
  var context = canvas.getContext('2d');
  context.clearRect(0, 0, canvas.width, canvas.height);
  new_fabric();
};
