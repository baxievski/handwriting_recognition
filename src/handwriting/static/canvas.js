var canvas = new fabric.Canvas('sheet');
canvas.isDrawingMode = true;
canvas.freeDrawingBrush.width = 20;
canvas.freeDrawingBrush.color = "#000000";

function send_image_data() {
  $('form input[name=image_data]').val(sheet.toDataURL("image/png"));
  $('form input[name=width]').val(sheet.width);
  $('form input[name=height]').val(sheet.height);
  $('form').submit();
}

function clear_canvas() {
  canvas.clear();
}
