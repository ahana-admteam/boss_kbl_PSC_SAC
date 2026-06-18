getPagination("#table-id");
$("#maxRows").trigger("change");
function getPagination(table) {
  $("#maxRows").on("change", function () {
    $(".pagination").html(""); // reset pagination div
    var trnum = 0; // reset tr counter
    var maxRows = parseInt($(this).val()); // get Max Rows from select option

    var totalRows = $(table + " tbody tr").length; // numbers of rows
    $(table + " tr:gt(0)").each(function () {
      // each TR in  table and not the header
      trnum++; // Start Counter
      if (trnum > maxRows) {
        // if tr number gt maxRows

        $(this).hide(); // fade it out
      }
      if (trnum <= maxRows) {
        $(this).show();
      } // else fade in Important in case if it ..
    }); //  was fade out to fade it in
    if (totalRows > maxRows) {
      // if tr total rows gt max rows option
      var pagenum = Math.ceil(totalRows / maxRows); // ceil total(rows/maxrows) to get ..
      //	numbers of pages
      for (var i = 1; i <= pagenum; ) {
        // for each page append pagination li
        $(".pagination")
          .append(
            '<li data-page="' +
              i +
              '">\
                                  <span>' +
              i++ +
              '<span class="sr-only">(current)</span></span>\
                                </li>'
          )
          .show();
      } // end for i
    } // end if row count > max rows
    $(".pagination li:first-child").addClass("active"); // add active class to the first li

    //SHOWING ROWS NUMBER OUT OF TOTAL DEFAULT
    showig_rows_count(maxRows, 1, totalRows);
    //SHOWING ROWS NUMBER OUT OF TOTAL DEFAULT

    $(".pagination li").on("click", function (e) {
      // on click each page
      e.preventDefault();
      var pageNum = $(this).attr("data-page"); // get it's number
      var trIndex = 0; // reset tr counter
      $(".pagination li").removeClass("active"); // remove active class from all li
      $(this).addClass("active"); // add active class to the clicked

      //SHOWING ROWS NUMBER OUT OF TOTAL
      showig_rows_count(maxRows, pageNum, totalRows);
      //SHOWING ROWS NUMBER OUT OF TOTAL

      $(table + " tr:gt(0)").each(function () {
        // each tr in table not the header
        trIndex++; // tr index counter
        // if tr index gt maxRows*pageNum or lt maxRows*pageNum-maxRows fade if out
        if (
          trIndex > maxRows * pageNum ||
          trIndex <= maxRows * pageNum - maxRows
        ) {
          $(this).hide();
        } else {
          $(this).show();
        } //else fade in
      }); // end of for each tr in table
    }); // end of on click pagination list
  });
}



function showig_rows_count(maxRows, pageNum, totalRows) {
  var end_index = maxRows * pageNum;
  var start_index = maxRows * pageNum - maxRows + parseFloat(1);

  if(end_index<totalRows){
  var string =
    "Showing " +

    end_index +
    " of " +
    totalRows +
    " entries";
	}
	else{
		var string =
    "Showing " +

    totalRows +
    " of " +
    totalRows +
    " entries";
	}

  $(".rows_count").html(string);

}



function FilterkeyWord_all_table() {
  var count = $(".table")
    .children("tbody")
    .children("tr:first-child")
    .children("td").length;
  var input, filter, table, tr, td, i;
  input = document.getElementById("search_input_all");
  var input_value = document.getElementById("search_input_all").value;
  filter = input.value.toLowerCase();
  if (input_value != "") {
    table = document.getElementById("table-id");
    tr = table.getElementsByTagName("tr");
    for (i = 1; i < tr.length; i++) {
      var flag = 0;

      for (j = 0; j < count; j++) {
        td = tr[i].getElementsByTagName("td")[j];
        if (td) {
          var td_text = td.innerHTML;
          if (td.innerHTML.toLowerCase().indexOf(filter) > -1) {
            flag = 1;
          } else {
          }
        }
      }
      if (flag == 1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  } else {
    $("#maxRows").trigger("change");
  }
}

function FilterkeyWord_all_table1() {
  console.log('search')
  var count = $(".table")
    .children("tbody")
    .children("tr:first-child")
    .children("td").length;
  var input, filter, table, tr, td, i;
  input = document.getElementById("search_input_all1");
  var input_value = document.getElementById("search_input_all1").value;
  filter = input.value.toLowerCase();
  if (input_value != "") {
    table = document.getElementById("table-id1");
    tr = table.getElementsByTagName("tr");
    for (i = 1; i < tr.length; i++) {
      var flag = 0;

      for (j = 0; j < count; j++) {
        td = tr[i].getElementsByTagName("td")[j];
        if (td) {
          var td_text = td.innerHTML;
          if (td.innerHTML.toLowerCase().indexOf(filter) > -1) {
            flag = 1;
          } else {
          }
        }
      }
      if (flag == 1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  } else {
    $("#maxRows").trigger("change");
  }
}

function FilterkeyWord_all_table2() {
  var count = $(".table")
    .children("tbody")
    .children("tr:first-child")
    .children("td").length;
  var input, filter, table, tr, td, i;
  input = document.getElementById("search_input_all2");
  var input_value = document.getElementById("search_input_all2").value;
  filter = input.value.toLowerCase();
  if (input_value != "") {
    table = document.getElementById("table-id2");
    tr = table.getElementsByTagName("tr");
    for (i = 1; i < tr.length; i++) {
      var flag = 0;

      for (j = 0; j < count; j++) {
        td = tr[i].getElementsByTagName("td")[j];
        if (td) {
          var td_text = td.innerHTML;
          if (td.innerHTML.toLowerCase().indexOf(filter) > -1) {
            flag = 1;
          } else {
          }
        }
      }
      if (flag == 1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  } else {
    $("#maxRows").trigger("change");
  }
}

// GENERIC EXPORT DATE VALIDATION

$('#submit_export').on('click', function (e) { 
  var from_date = $('#export_fromdate').val();
  var to_date = $('#export_todate').val();  
  var start_month = new Date(from_date).getMonth()+1
  var start_month1 = new Date(to_date).getMonth()+1
  var end_month = new Date(to_date).getMonth()+1
  var start_year = new Date(from_date).getFullYear()
  var start_year1 = new Date(from_date).getFullYear()+1
  var end_year = new Date(to_date).getFullYear()
  print(from_date,to_date)

  if (start_year==end_year) {
      $('#newModal_export').hide();
      window.location.reload(); 
  } 
  else if(end_year>start_year1){
      $('#date_msg').text("Your ToDate should not exceed more than 12 months from the FromDate.")
      $('#date_err_msg').show(); 
      e.preventDefault();
  }
  else if (start_year!=end_year && end_month>start_month ) {
      $('#date_msg').text("Your ToDate should not exceed more than 12 months from the FromDate.")
      $('#date_err_msg').show();
      e.preventDefault();      
  }  
  else{
      $('#newModal_export').hide();
      window.location.reload();  
  }              
});


$('#export_fromdate').on('change', function (e){
  
  var _todate = $('#export_fromdate').val();
  var dtToday = new Date(_todate);
  var month = dtToday.getMonth() + 1 ;
  var month1 = dtToday.getMonth() + 8 ;
  var day = dtToday.getDate();
  var year = dtToday.getFullYear();

  var today = new Date();
  var today_day = today.getDate();
  var today_month = today.getMonth() + 1;
  var today_year = today.getFullYear();


  if(month < 10 | month1 < 10)
      month = '0' + month.toString();
      month1 = '0' + month1.toString();
      console.log(month,month1)
  if(day < 10)
      day = '0' + day.toString();
  var minDate = year + '-' + month + '-' + day;
  var maxDate = today_year + '-' + today_month + '-' + today_day;
  
  $('.export_date_validity').attr('max', maxDate);
  document.getElementById("export_todate").setAttribute("min", minDate);        
});
  