//Takes a comma seperated list of progress stages and builds an html table in the style of a progress bar.
//'!' is placed as a list item in front of the current stage.
//(for the service this was built for, each feature had different stages)
//Example:
//Stage 1, Stage 2, !, Stage 3, Stage 4


var status = Split($datapoint.progress,', ')
var html = '<table style="border-collapse: separate; border-spacing: 2px 4px; margin: 0px -2px; max-width: 100%; table-layout: fixed; width: 100%;"><tbody><tr>';
var mid_html = '</tr><tr>';
var end_html = '</tr></tbody></table>';

var n = 0;

for (var z in status) {
    if (status[z] == '!') {n = z+1}
    }

function getStat(stat) {
    var spot = IndexOf(status, stat)
    if (spot < n) {return '#50C878'}
    if (spot == n) {return '#0000FF'}
    if (spot > n) {return '#ffffff'}
}

function getSym(stat) {
    var spot = IndexOf(status, stat)
    if (spot < n) {return '✔'}
    if (spot == n) {return '...'}
    if (spot > n) {return '&nbsp;'}
}



for(var i=0; i<Count(status); i++)
if (status[i] != '!') {
    html = html+'<td style="text-align: center; width: 25%; background-color: '+getStat(status[i])+';">'+getSym(status[i])+'</td>'
}

html = html + mid_html

for (var x in status) {
    if (status[x] != '!') {
    html = html+'<td style="text-align: center; width: 25%; padding: 0px; opacity: 0.7; word-wrap: break-word; font-size: 8px">'+status[x]+'</td>'
}}

html = html + end_html


return {
  textColor: '',
  backgroundColor: '',
  separatorColor:'#001242',
  selectionColor: '##001242',
  selectionTextColor: '',
  attributes: {
    progressbar: html
  }
}
