let files = [];
files_length = files.length
function fileData(data) {
  files.push(...data);
  $("#file_values").val(JSON.stringify(files));
  // console.log('fileszzzz',files);
  return files
}


function deleteRow(sectionName, rowIndex) {
  rowcnt = $('#rowcnt').val()
  // rowcnt = rowIndex;
  console.log('@@@@@@@@',sectionName,rowIndex);
  // if (sectionName == section.value) {
    
 
  //document.getElementById("myTable").deleteRow(rowcnt);
  const previousSecondElementOfTheArray = files.splice((rowcnt - 1), 1);
  // console.log("on delete click", previousSecondElementOfTheArray)
  if (previousSecondElementOfTheArray[0]['document_id']) {

    // console.log(previousSecondElementOfTheArray, files, previousSecondElementOfTheArray[0]['document_id']); // [2]
    var csrftoken = $("[name=csrfmiddlewaretoken]").val();
    $.ajax({
      type: "POST",
      url: '/deletefile/',
      headers: {
        "X-CSRFToken": csrftoken
      },
      cache: false,
      data: {
        'file_id': previousSecondElementOfTheArray[0]['document_id'],
        'review_id': '1',
        'review_type': '1'
      },
      success: function (data) {
        // console.log(data, 'jhjkhkjh')
        //$('#success').show()
        if (data === 'success') {
          // alert('delll')
          // $('#delete_file_msg').show();
          const index = files.indexOf(previousSecondElementOfTheArray);
          if (index > -1) { // only splice array when item is found
            files.splice(index, 1); // 2nd parameter means remove one item only
          }
          $("#myTable").find("tr:not(:first)").remove();

          files.forEach(function (element, index) {
            
            // console.log("element values delete row", element)
            var table = document.getElementById("myTable");
            var rowCount = table.rows.length;
            
            var row = table.insertRow(rowCount);


            //row.setAttribute("data-section", element.section);

            row.insertCell(0).innerHTML =
              `
                        <td style="word-wrap: break-word;">
                            <span>
                                ` +
              element.file_name +
              `
                            </span>    
                        </td>
                    `;

            row.insertCell(1).innerHTML =
              `
                        <td>
                        <span >
                                ` +
              element.section +
              `
                            </span>    
                        </td>
                    `;

            row.insertCell(2).innerHTML =
              `
                        <td>
                            <div class="col-md-8">
                    <div class="row d-flex justify-content-center">
                        <div style="max-width: 29%;" >
                                        <button class="form-control btn-outline-primary" onclick="openimg(\'` +
              element.file +
              `\',\'` +
              element.file_type +
              `\',\'` +
              element.document_id +
              `\')">Preview</button>
                                    </div>    
                                    <div style="max-width: 29%;"  >
                                        <button   class="form-control btn-outline-primary deletefile" id=`+element.section+`  data-toggle="modal" data-target="#myModal" onclick="getrowcnt(\'` + rowCount + `\')">Delete</button>
                                    </div>    
                                </div>    
                            </div>    
                        </td>
                    `
          })
        }
        $('#file_values').val(JSON.stringify(files))
        // document.getElementById(section+'-file_values').value = [];

      }
    });

  }
  const index = files.indexOf(previousSecondElementOfTheArray);
  if (index > -1) { // only splice array when item is found
    files.splice(index, 1); // 2nd parameter means remove one item only
  }
  $("#myTable").find("tr:not(:first)").remove();

  files.forEach(function (element, index) {
    // console.log("element values delete row files iasdaddqw", element)
    var table = document.getElementById("myTable");
    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);

    //row.setAttribute("data-section", element.section);



    row.insertCell(0).innerHTML =
      `
            <td style="word-wrap: break-word;">
                <span>
                    ` +
      element.file_name +
      `
                </span>    
            </td>
        `;

    row.insertCell(1).innerHTML =
      `
            <td>
            <span >
                    ` +
      element.section +
      `
                </span>    
            </td>
        `;

    row.insertCell(2).innerHTML =
      `
            <td>
                <div class="col-md-8">
                    <div class="row d-flex justify-content-center">
                        <div style="max-width: 29%;" >
                            <button class="form-control btn-outline-primary" onclick="openimg(\'` +
      element.file +
      `\',\'` +
      element.file_type +
      `\',\'` +
      element.document_id +
      `\')">Preview</button>
                        </div>    
                        <div style="max-width: 29%;"  >
                            <button  class="form-control btn-outline-primary deletefile" id=`+element.section+` data-toggle="modal" data-target="#myModal" onclick="getrowcnt(\'` + rowCount + `\')">Delete</button>
                        </div>    
                    </div>    
                </div>    
            </td>
        `


  })

  $('#file_values').val(JSON.stringify(files))
  
  if (files.length != files_length) {
    // console.log("files valuesd")
    $('#uploadfileContainer').show();
    window.onload = setTimeout(function () {
      alert('File deleted succesfully')
    }, 500)
    checkTableRowCount();
    // console.log(currentUser);
    // console.log(permitteduser);
    console.log('uploadButton',uploadButton);
    if(uploadButton){
    document.getElementById(uploadButton).innerHTML = '<i class="fa fa-upload"></i>'
    $('#fileUploadModal1').modal('hide');
  }
    files_length = files
    // Function to fetch unique sections
function fetchUniqueSections(data) {
  var sections = [];
  data.forEach(function(item) {
      if (!sections.includes(item.section)) {
          sections.push(item.section);
      }
  });
  return sections;
}

// Fetch unique sections
var uniqueSections = fetchUniqueSections(files_length);
console.log(uniqueSections); // Output: ["Data", "Analysis"]
    console.log('files_length',files_length);
  }
// }
// else{
//     alert('Cannont be deleted as it does not belong to the selected section')
// }
}

function checkTableRowCount() {
  var table = document.getElementById("myTable");
  var rowCount = table.getElementsByTagName("tr").length;
  if (rowCount >= 2) {
      $('.docTable').show(); // Show the table container
  } else {
      $('.docTable').hide(); // Hide the table container
  }
}

function addFiles(file_name, file_type, file_data, section) {
  let fileValue = {
    file_name: "",
    file_type: "",
    section: "",
    document_id: "",
  };
  
  fileValue["file_name"] = file_name;
  fileValue["file_type"] = file_type;
  fileValue["file"] = file_data;
  fileValue["section"] = section;
  
  
  return fileValue;
}



async function previewFile(section) {
  const file = document.querySelector("input[type=file]").files[0];
  let dataURL = await convert2DataUrl(file);
  let base64Data = dataURL.split(",")[1];  
  let file_type_val = "";

  if (file.type === 'image/jpeg') {
    file_type_val = 'jpeg';
  } else if (file.type === "application/pdf") {
    file_type_val = 'pdf';
  } else if (file.type === "image/png") {
    file_type_val = 'png';
  } else {
    file_type_val = 'xlsx';
  }

  const found = files.some(el => el.section === section);
  // console.log('found',found);
  if (!found) {
    const found1 = files.some(el => el.file_name === file.name);
    
    if (!found1){
    let val = addFiles(file.name, file_type_val, base64Data, section);
    files.push(val);
    $('#file_values').val(JSON.stringify(files));
    // let data_json = files?.filter((obj)=>(obj.section===section))[0]
    // document.getElementById(section+'-file_values').value = JSON.stringify(data_json);
    $("#myTable").find("tr:not(:first)").remove();
    if (files.length != files_length) {
      // console.log("files values changed");
      files_length = files.length;
    }
    files.forEach(function (element, index) {
      var table = document.getElementById("myTable");
      var rowCount = table.rows.length;
      var row = table.insertRow(rowCount);
      //row.setAttribute("data-section", element.section);
      row.insertCell(0).innerHTML =
        `
                <td style="word-wrap: break-word;">
                    <span>
                        ` +
        element.file_name +
        `
                    </span>    
                </td>
            `;

      row.insertCell(1).innerHTML =
        `
                <td>
                <span>
                        ` +
        element.section +
        `
                    </span>    
                </td>
            `;

      row.insertCell(2).innerHTML =
        `
                <td>
                    <div class="col-md-8">
                    <div class="row d-flex justify-content-center">
                        <div style="max-width: 29%;" >
                                <button class="form-control btn-outline-primary" onclick="openimg(\'` +
        element.file +
        `\',\'` +
        element.file_type +
        `\',\'` +
        element.document_id +
        `\')">Preview</button>
                            </div>    
                            <div style="max-width: 29%;"  >
                                <button  class="form-control btn-outline-primary deletefile" id=`+element.section+` data-toggle="modal" data-target="#myModal" onclick="getrowcnt(\'` + rowCount + `\')">Delete</button>
                            </div>    
                        </div>    
                    </div>    
                </td>
            `;
    });
    $('#uploadfileContainer').hide();
      const a = document.getElementById(section).id;
    // console.log(a,typeof(a));
    uploadButton = a.charAt(0).toLowerCase() + a.slice(1);
    // console.log('jhvfhjfjh',uploadButton);
    $('#fileUploadModal1').modal('hide');
    document.getElementById(uploadButton).innerHTML = 'Uploaded'
    checkTableRowCount();
    // console.log(currentUser);
    // console.log(permitteduser);

  }
  else{
    alert('File exists in other section')
  } 
}
else {
    alert('File has been already uploaded for the selected section');
  }

}



// function openimg1(a, b, c) {
//   let document_id = parseInt(c);
//   console.log(a);
//   if (document_id > 0) {
//     let src = "";

//     $.ajax({
//       type: "GET",
//       url: "/boss_admin/viewfile",
//       data: {
//         document_id: document_id,
        
//       },
//       success: function (data) {
//         let a = data["file"];
//         let b = data["file_type"];
//         console.log('a,b',a,b);
//         if (b == "xlsx") {
//           var contentType =
//             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
//           var blob1 = b64toBlob(a, contentType);
//           var blobUrl1 = URL.createObjectURL(blob1);

//           window.open(blobUrl1);

//           function b64toBlob(b64Data, contentType, sliceSize) {
//             contentType = contentType || "";
//             sliceSize = sliceSize || 512;

//             var byteCharacters = atob(b64Data);
//             var byteArrays = [];

//             for (
//               var offset = 0;
//               offset < byteCharacters.length;
//               offset += sliceSize
//             ) {
//               var slice = byteCharacters.slice(offset, offset + sliceSize);

//               var byteNumbers = new Array(slice.length);
//               for (var i = 0; i < slice.length; i++) {
//                 byteNumbers[i] = slice.charCodeAt(i);
//               }

//               var byteArray = new Uint8Array(byteNumbers);

//               byteArrays.push(byteArray);
//             }

//             var blob = new Blob(byteArrays, { type: contentType });
//             return blob;
//           }
//         } else if (b == "pdf") {
//           var windo = window.open("image", "");
//           var objbuilder = "";
//           objbuilder +=
//             "<embed width='100%' height='100%'  src=\"data:application/pdf;base64,";
//           objbuilder += a;
//           objbuilder += '" type="application/pdf" />';
//           windo.document.write(objbuilder);
//         } else if (b == "png" || b == "jpeg" || b == "jpg") {
//           if (b == "jpg") {
//             b = "jpeg";
//           }

//           var windo = window.open("", "");
//           var objbuilder = "";
//           objbuilder +=
//             "<embed width='100%' height='100%'  src=\"data:image/" +
//             b +
//             ";base64,";
//           objbuilder += a;
//           objbuilder += '" type="image/' + b + '" />';
//           windo.document.write(objbuilder);
//         }
//       },
//     });
//   } else {
//     let src = "";
//     if (b == "xlsx") {
//       var contentType =
//         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
//       var blob1 = b64toBlob(a, contentType);
//       var blobUrl1 = URL.createObjectURL(blob1);

//       window.open(blobUrl1);

//       function b64toBlob(b64Data, contentType, sliceSize) {
//         contentType = contentType || "";
//         sliceSize = sliceSize || 512;

//         var byteCharacters = atob(b64Data);
//         var byteArrays = [];

//         for (
//           var offset = 0;
//           offset < byteCharacters.length;
//           offset += sliceSize
//         ) {
//           var slice = byteCharacters.slice(offset, offset + sliceSize);

//           var byteNumbers = new Array(slice.length);
//           for (var i = 0; i < slice.length; i++) {
//             byteNumbers[i] = slice.charCodeAt(i);
//           }

//           var byteArray = new Uint8Array(byteNumbers);

//           byteArrays.push(byteArray);
//         }

//         var blob = new Blob(byteArrays, { type: contentType });
//         return blob;
//       }
//     } else if (b == "pdf") {
//       var windo = window.open("image", "");
//       var objbuilder = "";
//       objbuilder +=
//         "<embed width='100%' height='100%'  src=\"data:application/pdf;base64,";
//       objbuilder += a;
//       objbuilder += '" type="application/pdf" />';
//       windo.document.write(objbuilder);
//     } else if (b == "png" || b == "jpeg" || b == "jpg") {
//       if (b == "jpg") {
//         b = "jpeg";
//       }

//       var windo = window.open("", "");
//       var objbuilder = "";
//       objbuilder +=
//         "<embed width='100%' height='100%'  src=\"data:image/" + b + ";base64,";
//       objbuilder += a;
//       objbuilder += '" type="image/' + b + '" />';
//       windo.document.write(objbuilder);
//     }
//   }
// }


function openimg(a, b, c) {
  let document_id = parseInt(c);
  // console.log(a,'file');
  if (document_id > 0) {
    let src = "";

    $.ajax({
      type: "GET",
      url: "/viewfile",
      data: {
        document_id: document_id,
        
      },
      success: function (data) {
        // console.log('success',data);
        try {
          let a = data.file_data[0].file
          let b = data.file_data[0].file_type

          // let b = data[0].file_type;
          // console.log('a,b',a);
          if (b == "xlsx") {
            var contentType =
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
            var blob1 = b64toBlob(a, contentType);
            var blobUrl1 = URL.createObjectURL(blob1);

            window.open(blobUrl1);

            function b64toBlob(b64Data, contentType, sliceSize) {
              contentType = contentType || "";
              sliceSize = sliceSize || 512;

              var byteCharacters = atob(b64Data);
              var byteArrays = [];

              for (
                var offset = 0;
                offset < byteCharacters.length;
                offset += sliceSize
              ) {
                var slice = byteCharacters.slice(offset, offset + sliceSize);

                var byteNumbers = new Array(slice.length);
                for (var i = 0; i < slice.length; i++) {
                  byteNumbers[i] = slice.charCodeAt(i);
                }

                var byteArray = new Uint8Array(byteNumbers);

                byteArrays.push(byteArray);
              }

              var blob = new Blob(byteArrays, { type: contentType });
              return blob;
            }
          } else if (b == "pdf") {
            var windo = window.open("image", "");
            var objbuilder = "";
            objbuilder +=
              "<embed width='100%' height='100%'  src=\"data:application/pdf;base64,";
            objbuilder += a;
            objbuilder += '" type="application/pdf" />';
            windo.document.write(objbuilder);
          } else if (b == "png" || b == "jpeg" || b == "jpg") {
            if (b == "jpg") {
              b = "jpeg";
            }

            var windo = window.open("", "");
            var objbuilder = "";
            objbuilder +=
              "<embed width='100%' height='100%'  src=\"data:image/" +
              b +
              ";base64,";
            objbuilder += a;
            objbuilder += '" type="image/' + b + '" />';
            windo.document.write(objbuilder);
          }
        } catch (error) {
          console.error("Error processing AJAX success:", error);
        }
      },
      error: function (xhr, status, error) {
        console.error("AJAX Error:", error);
      }
    });
  } else {
    console.log('else');
    let src = "";
    if (b == "xlsx") {
      var contentType =
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";
      var blob1 = b64toBlob(a, contentType);
      var blobUrl1 = URL.createObjectURL(blob1);

      window.open(blobUrl1);

      function b64toBlob(b64Data, contentType, sliceSize) {
        contentType = contentType || "";
        sliceSize = sliceSize || 512;

        var byteCharacters = atob(b64Data);
        var byteArrays = [];

        for (
          var offset = 0;
          offset < byteCharacters.length;
          offset += sliceSize
        ) {
          var slice = byteCharacters.slice(offset, offset + sliceSize);

          var byteNumbers = new Array(slice.length);
          for (var i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
          }

          var byteArray = new Uint8Array(byteNumbers);

          byteArrays.push(byteArray);
        }

        var blob = new Blob(byteArrays, { type: contentType });
        return blob;
      }
    } else if (b == "pdf") {
      var windo = window.open("image", "");
      var objbuilder = "";
      objbuilder +=
        "<embed width='100%' height='100%'  src=\"data:application/pdf;base64,";
      objbuilder += a;
      objbuilder += '" type="application/pdf" />';
      windo.document.write(objbuilder);
    } else if (b == "png" || b == "jpeg" || b == "jpg") {
      if (b == "jpg") {
        b = "jpeg";
      }

      var windo = window.open("", "");
      var objbuilder = "";
      objbuilder +=
        "<embed width='100%' height='100%'  src=\"data:image/" + b + ";base64,";
      objbuilder += a;
      objbuilder += '" type="image/' + b + '" />';
      windo.document.write(objbuilder);
    }
  }
}


async function convert2DataUrl(blobOrFile) {
  let reader = new FileReader();
  reader.readAsDataURL(blobOrFile);
  await new Promise((resolve) => (reader.onload = () => resolve()));
  return reader.result;
}
function getrowcnt(a) {
  $('#rowcnt').val(a)
}




   