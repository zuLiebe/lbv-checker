function reload() {
  location.reload();
}

/*
    Function: nurZiffern
      lässt im Eingabefeld nur Ziffern zu

    Parameters:
      die HTML-ID des Eingabefelds

    Returns:
      nichts
  */
function nurZiffern(eingabefeld) {
  var id = document.getElementById(eingabefeld);
  if (null != id) {
    id.value = id.value.replace(/[^\d]/g, '');
  }
}

/*
  Function: nurBuchstaben
    lässt im Eingabefeld nur Buchstaben zu

  Parameters:
    die HTML-ID des Eingabefelds

  Returns:
    nichts
*/
function nurBuchstaben(eingabefeld) {
  var id = document.getElementById(eingabefeld);
  if (null != id) {
    id.value = id.value.replace(/[^a-zäöüßA-ZÄÖÜ]/g, '');
  }
}

/*
  Function: nurBuchstaben
    lässt im Eingabefeld nur Buchstaben zu

  Parameters:
    die HTML-ID des Eingabefelds

  Returns:
    nichts
*/
function nurBuchstabenHE(eingabefeld) {
  var id = document.getElementById(eingabefeld);
  if (null != id) {
    id.value = id.value.replace(/[^HE]/g, '');
  }
}


/*
  Function: nurZiffernUndBuchstaben
    lässt im Eingabefeld nur Ziffern und Buchstaben zu

  Parameters:
    die HTML-ID des Eingabefelds

  Returns:
    nichts
*/
function nurZiffernUndBuchstaben(eingabefeld) {
  var id = document.getElementById(eingabefeld);
  if (null != id) {
    id.value = id.value.replace(/[^a-zäöüßA-ZÄÖÜ\d]/g, '');
  }
}




function show(elemID) {
  var elem = document.getElementById(elemID);
  if (null != elem) {
    elem.style.setProperty('display', 'block', 'important');
  }
}

function hide(elemID) {
  var elem = document.getElementById(elemID);
  if (null != elem) {
    elem.style.display = "none";
  }
}

function showByName(elemname) {
  elemarray = document.getElementsByName(elemname)
  for (var i = 0; i < elemarray.length; ++i) {
    elemarray[i].style.display = "block";
  }
}

function hideElementsStartingWith(prefix, containerId) {
  // Den Container mit der gegebenen ID finden
  const container = document.getElementById(containerId);
  
  if (!container) {
    console.error(`Container mit der ID "${containerId}" nicht gefunden.`);
    return;
  }
  
  // Alle Elemente im Container durchsuchen
  const elements = container.querySelectorAll('*');
  
  // Durch alle gefundenen Elemente iterieren
  elements.forEach(element => {
    // Überprüfen, ob das Element einen Namen hat und dieser mit dem gegebenen Präfix beginnt
    let elementName = element.getAttribute('name') || element.id;
    
    if (elementName && elementName.startsWith(prefix)) {
      // Das Element ausblenden
      element.style.display = 'none';
    }
  });
}


function setContent(elemID, content) {
  var elem = document.getElementById(elemID);
  if (null != elem) {
    elem.innerHTML = content;
  }
}

function addContent(elemID, content) {
  var elem = document.getElementById(elemID);
  if (null != elem) {
    elem.innerHTML += content;
  }
}

function toggle(elemID) {
  var elem = document.getElementById(elemID);
  if (null != elem) {
    if (elem.style.display == "block") {
      elem.style.display = "none";
    }
    else {
      //elem.style.display = "block";    
      elem.style.setProperty('display', 'block', 'important');
    }
  }
}

function togglemodal(elemid) {
  //console.log("show #"+elemid);
  $("#"+elemid).modal('show');
}

function hidemodal(elemid) {  
  console.log("hide #"+elemid);
  $("#"+elemid).modal('hide');
  modalInstance = new bootstrap.Modal(document.getElementById(elemid));
  modalInstance.hide();
}


function togglePlusMinus(elemID) {
  var elem = document.getElementById(elemID);
  if (null != elem) {
    if (elem.innerHTML == "&nbsp;+&nbsp;") {
      elem.innerHTML = "&nbsp;&ndash;&nbsp;";
    }
    else {
      elem.innerHTML = "&nbsp;+&nbsp;";
    }
  }
}

function hideAll(classname) {
  var elems = document.getElementsByClassName(classname);
  for (var i = 0; i < elems.length; ++i) {
    elems[i].style.display = "none";
  }
}

function jump(h) {
  var url = location.href;               //Save down the URL without hash.
  location.href = "#" + h;                 //Go to the target element.
  history.replaceState(null, null, url);   //Don't like hashes. Changing it back.
}


function callURL(url, newwindow) {
  if (typeof newwindow == "undefined") {
    newwindow = false;
  }
  if (newwindow) {
    window.open(url, '_blank');
  } else {
    window.location = url;
  }
}


function checkcheckbox(elem, weiterbutton) {
  if (document.getElementById(elem).checked) {
    document.getElementById(weiterbutton).disabled = false;
  }
  else {
    document.getElementById(weiterbutton).disabled = true;
  }
}

function checkfirma() {
  if (this.document.getElementById("firma").value == "sonstige") {
    this.document.getElementById("firmafreitextgroup").style.setProperty('display', 'block', 'important');
  }
  else {
    this.document.getElementById("firmafreitextgroup").style.setProperty('display', 'none', 'important');
    clearValue("firmafreitextgroup");
  }
  clearValue("vorname");
}

function clearnotrequired(elem) {
  if (!document.getElementById(elem).required) {
    document.getElementById(elem).value = "";
  }
}


function clearValue(elem) {
  this.document.getElementById(elem).value = "";
}

function switchcheckbox(elem, show, hide) {
  if (document.getElementById(elem).checked) {
    document.getElementById(show).style.setProperty('display', 'block', 'important');
    setRequired(show, true);
    document.getElementById(hide).style.setProperty('display', 'none', 'important');
    setRequired(hide, false);
  }
  else {
    document.getElementById(hide).style.setProperty('display', 'block', 'important');
    setRequired(hide, true);
    document.getElementById(show).style.setProperty('display', 'none', 'important');
    setRequired(show, false);
  }
}

function setlabel(checkbox, elem, label, labelchecked) {
  var elemlabel = elem + "label";
  if (document.getElementById(checkbox).checked) {
    document.getElementById(elem).placeholder = labelchecked;
    document.getElementById(elemlabel).innerText = labelchecked;
  }
  else {
    document.getElementById(elem).placeholder = label;
    document.getElementById(elemlabel).innerText = label;
  }
}

function setvertretung(elem) {
  if (elem.checked) {
    show('vollmachtangabe');
    setRequiredById('vollmacht_vorname', true);
    setRequiredById('vollmacht_nachname', true);
    setChecked('othercheckbox', true);
    setChecked('mecheckbox', false);
    hide('choiceme');
  } else {
    hide('vollmachtangabe');
    setRequiredById('vollmacht_vorname', false);
    setRequiredById('vollmacht_nachname', false);
    setChecked('othercheckbox', false);
    setChecked('mecheckbox', true);
    document.getElementById('choiceme').style.display = "inline";
  }
}

function setrepresentation(value) {
  if (value) {
    show('vollmachtangabe');
    setRequiredById('vollmacht_vorname', true);
    setRequiredById('vollmacht_nachname', true);
    setChecked('othercheckbox', true);
    setChecked('mecheckbox', false);
    hide('choiceme');
  } else {
    hide('vollmachtangabe');
    setRequiredById('vollmacht_vorname', false);
    setRequiredById('vollmacht_nachname', false);
    setChecked('othercheckbox', false);
    setChecked('mecheckbox', true);
    try {
      document.getElementById('choiceme').style.display = "inline";
    } catch (e) { }
  }
}



function setRequired(elem, val) {
  try {
    input = document.getElementById(elem).getElementsByTagName('input');
    for (i = 0; i < input.length; ++i) {
      input[i].required = val;
    }
    input = document.getElementById(elem).getElementsByTagName('select');
    for (i = 0; i < input.length; ++i) {
      input[i].required = val;
    }
  } catch (e) { }
}


function setRequiredById(elem, val) {
  try {
    var item = document.getElementById(elem)
    item.required = val;
/*
    if (val && item.nodeName == "INPUT") {
      item.setAttribute("data-pc-user","");
    } else {
      item.removeAttribute("data-pc-user");
    }
*/      
  } catch (e) { }
}



function setChecked(elem, val) {
  try {
    input = document.getElementById(elem).checked = val;
  } catch (e) { }

}


function setborder(id, name, classname) {
  var x = document.getElementsByName(name);
  var i;
  for (i = 0; i < x.length; i++) {
    x[i].style.border = "3px solid white";
    x[i].style.color = "#005ca9";
    x[i].style.backgroundColor = "white";
    x[i].classList.add("bluetext");
    x[i].classList.add("whiteborder");
  }
  var y = document.getElementsByClassName(classname);
  var i;
  for (i = 0; i < y.length; i++) {
    y[i].style.border = "3px solid white";
    y[i].style.color = "#005ca9";
    y[i].style.backgroundColor = "lightcoral";
    y[i].classList.add("bluetext");
    y[i].classList.add("whiteborder");
  }
  var elem = document.getElementById(id);
  elem.classList.remove("bluetext");
  elem.classList.remove("whiteborder");
  elem.style.border = "3px solid #007bff";
  elem.style.color = "white";
  elem.style.backgroundColor = "#007bff";
}

function setborderOnEnter(event, id, name, classname) {
  if (event.keyCode == 13) {
    setborder(id, name, classname);
  }
}

function setValue(id, value) {
  document.getElementById(id).value = value;
}

function setValueOnEnter(event, id, value) {
  if (event.keyCode == 13) {
    setValue(id, value);
  }
}

function enable(id) {
  document.getElementById(id).disabled = false;
}

function enableOnEnter(event, id) {
  if (event.keyCode == 13) {
    enable(id);
  }
}


function nurZiffernUndPlus(id) {
  korrekt = "";
  eingabefeld = this.document.getElementById(id);
  StrLen = eingabefeld.value.length;
  for (var i = 0; i < StrLen; i++) {
    if (!isNaN(eingabefeld.value.substr(i, 1)) || eingabefeld.value.substr(i, 1) === '+') {
      korrekt += eingabefeld.value.substr(i, 1);
    }
  }
  eingabefeld.value = korrekt;
}

function notempty(id) {
  value = document.getElementById(id).value;
  if (value.length > 0) return true;
  return false;
}

function checkbirthday(id) {
  result = true;
  elem = document.getElementById(id);
  const today = new Date();
  let year = today.getFullYear();
  if (parseInt(elem.value.substring(0, 4)) > (parseInt(year) - 11)) {
    alert("\nÜberprüfen Sie bitte Ihr Geburtsdatum \n\nPlease check your date of birth");
    result = false;
  }
  return result;
}

function checkinputlength(id, length) {
  result = true;
  elem = document.getElementById(id);
  if (elem.value.length != length) {
    alert("\nBitte tragen Sie die letzten 6 Ziffern der Fahrzeugidentifikationsnummer ein.");
    result = false;
  }
  return result;
}

function checkInput() {
  result = checkbirthday('geburtstag') && checkinputlength('fin', 6);
  return result;
}

function pleaseWait(htmltext) {
  let fullHeight = Math.max(
    document.body.scrollHeight,
    document.documentElement.scrollHeight,
    document.body.offsetHeight,
    document.documentElement.offsetHeight,
    document.body.clientHeight,
    document.documentElement.clientHeight
  );
  var elem = document.createElement('div');
  elem.style.cssText = 'position:absolute;width:100vw;height:'+fullHeight+'px;opacity:0.3;z-index:100;background:#000;top:0em;transition:opacity 5s;';
  var hinweis = document.createElement('div');
  hinweis.innerHTML = htmltext;
  hinweis.style.cssText = 'position:fixed;width:auto;z-index:101;background:#FFF;top: 40%;text-align: center;line-height: 3em; left: 40%; border: 4px gray outset; border-radius: 1em; padding: 2em;opacity:0.0;transition:opacity 1s;';
  document.body.appendChild(elem);
  document.body.appendChild(hinweis);
  window.setTimeout(function () { elem.style.opacity = "0.7"; }, 50);
  window.setTimeout(function () { hinweis.style.opacity = "1.0"; }, 500);
}



function startTimer(duration, elem) {
  display = document.getElementById(elem);
  var timer = duration, minutes, seconds;
  setInterval(function () {
    minutes = parseInt(timer / 60, 10);
    seconds = parseInt(timer % 60, 10);

    minutes = minutes < 10 ? "0" + minutes : minutes;
    seconds = seconds < 10 ? "0" + seconds : seconds;

    if (minutes >= 0 && seconds >= 0) {
      display.textContent = minutes + ":" + seconds;
    }
    else {
      display.textContent = "00:00";
    }
    --timer;
    /*        if (--timer < 0) {
                timer = duration;
            }*/
  }, 1000);
}



function startSessionTimer(duration, elem) {
  display = document.getElementById(elem);
  var sessionkey = Math.random();
  var sessionvalue = Date.now(); // Timesstamp
  saveToSessionStorage(sessionkey, sessionvalue);
  var timer = duration, minutes, seconds;
  setInterval(function () {
    timer = duration - (Date.now() - getFromSessionStorage(sessionkey)) / 1000;
    minutes = parseInt(timer / 60, 10);
    seconds = parseInt(timer % 60, 10);

    minutes = minutes < 10 ? "0" + minutes : minutes;
    seconds = seconds < 10 ? "0" + seconds : seconds;

    if (minutes >= 0 && seconds >= 0) {
      display.textContent = minutes + ":" + seconds;
    }
    else {
      display.textContent = "00:00";
    }
  }, 1000);
}



function setActive(id, time) {
  elem = document.getElementById(id);
  setTimeout(function () {
    elem.classList.remove('not-active');
    document.getElementById('waithint').display = "none";
  }, (time * 60000));
}


function closeWindow() {
  window.close();
}




/*
  Function: getULofDl		
     
  Parameters:
    unterlagenid 
    language
  	
  Returns:
    nichts
*/
function getULofDl(id, anliegenid, language) {
  var elem = document.getElementById(id);
  if (elem.innerHTML.length < 5 && elem.style.display != "none") {
    var xmlhttp = new XMLHttpRequest();
    var currenturl = window.location.href;

    var url = currenturl.substring(0, currenturl.lastIndexOf('/')) + "/../ajax/unterlageneinesanliegens.php?anliegenid=" + anliegenid + "&language=" + language;

    xmlhttp.onreadystatechange = function () {
      if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
        var unterlagen = JSON.parse(xmlhttp.responseText);
        document.getElementById(id).innerHTML = unterlagen;
      }
    }
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
  }
}



/*
  Function: callOnEnter		
     
  Parameters:
    event 
    url
  	
  Returns:
    nichts
*/
function callOnEnter(event, url, newwindow) {
  if (typeof newwindow == "undefined") {
    newwindow = false;
  }
  if (event.keyCode == 13) {
    callURL(url, newwindow);
  }
}





/*
  Function: getZeiten
        holt die infrage kommenden Zeiten und stellt sie dar
     
  Parameters:
        dlid - die Dienstleistungsid
        standortid - die Standortid
        oidliste - die Liste der ÖffnungszeitenIDs
        datum - Datum
*/
function getZeiten(dlid, standortid, oidliste, datum, token) {
  var xmlhttp = new XMLHttpRequest();
  var currenturl = window.location.href;
  var url = currenturl.substring(0, currenturl.lastIndexOf('/')) + "/../ajax/zeitensammlung.php";
  var ausgabe = "";
  setContent('zeitenliste', "<span class=\"loading\"><img src=\"img/ajax-loading.gif\"></span>");
  xmlhttp.onreadystatechange = function () {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
      var zeiten = JSON.parse(xmlhttp.responseText);
      if (zeiten != "Fehler") {
        var letzteStunde = "";
        var zeitid = null;
        for (i = 0; i < zeiten.length; i++) {
          if (zeiten[i].buchbar) {
            /*            if (letzteStunde != "" && parseInt(letzteStunde) < parseInt(zeiten[i].zeit.substring(0, 2))) {
                          ausgabe += "<p style=\"\">&nbsp;</p>";
                        }*/
            if (parseInt(standortid) > 0) {
              ausgabe += "<div class=\"float-left mb-1 LBVBox-minwidth bluetext cursor-pointer hoverable whiteborder\" tabindex=\"0\" onkeyup=\"enableOnEnter(event, 'weiterbutton');setValueOnEnter(event, 'zeit', '" + zeiten[i].zeit + "'); setValueOnEnter(event, 'oid', '" + zeiten[i].oeffnungszeitid + "'); setValueOnEnter(event, 'stornobuergerid', ''); setborderOnEnter(event, '" + zeiten[i].zeit.substring(0, 5) + "', 'zeiten', 'stornotermin');\" onclick=\"enable('weiterbutton'); setValue('zeit', '" + zeiten[i].zeit + "'); setValue('stornobuergerid', ''); setValue('oid', '" + zeiten[i].oeffnungszeitid + "'); setborder('" + zeiten[i].zeit.substring(0, 5) + "', 'zeiten', 'stornotermin');\" name=\"zeiten\" id=\"" + zeiten[i].zeit.substring(0, 5) + "\"> " + zeiten[i].zeit.substring(0, 5) + " </div> ";
            }
            else {
              ausgabe += "<div class=\"float-left mb-1 LBVBox-minwidth bluetext cursor-pointer hoverable whiteborder\" tabindex=\"0\" onkeyup=\"enableOnEnter(event, 'weiterbutton');setValueOnEnter(event, 'zeit', '" + zeiten[i].zeit + "'); setValueOnEnter(event, 'oid', '" + zeiten[i].oeffnungszeitid + "'); setValueOnEnter(event, 'stornobuergerid', ''); setborderOnEnter(event, '" + zeiten[i].zeit.substring(0, 5) + "', 'zeiten', 'stornotermin');\" onclick=\"enable('weiterbutton'); setValue('zeit', '" + zeiten[i].zeit + "'); setValue('stornobuergerid', ''); setValue('oid', '" + zeiten[i].oeffnungszeitid + "'); setborder('" + zeiten[i].zeit.substring(0, 5) + "', 'zeiten', 'stornotermin');\" name=\"zeiten\" id=\"" + zeiten[i].zeit.substring(0, 5) + "\"> " + zeiten[i].zeit.substring(0, 5) + ": " + zeiten[i].standortname + " </div> ";
            }
            letzteStunde = zeiten[i].zeit.substring(0, 2);
            if (null == zeitid) {
              zeitid = zeiten[i].zeit.substring(0, 5);
            }
          }
        }
        setContent('zeitenliste', ausgabe);
        //var meindatum = new Date(datum.substr(0,4), datum.substr(5,2), datum.substr(8,2));     
        setContent('meindatum', datum.substr(8, 2) + '.' + datum.substr(5, 2) + '.' + datum.substr(0, 4));        
        setValue('datum', datum);
        try {
          document.getElementById(zeitid).focus();
        } catch(e){}
      }
      else {
        location.reload();
      }
    }
  }
  xmlhttp.open("POST", url, true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("anliegen[]=" + dlid + "&datum=" + datum + "&OID=" + oidliste + "&token=" + token);

}


/*
  Function: getZeitenOnEnter		
     
  Parameters:
    event 
    url
  	
  Returns:
    nichts
*/
function getZeitenOnEnter(event, dlid, standortid, oidliste, datum, token) {
  if (event.keyCode == 13) {
    getZeiten(dlid, standortid, oidliste, datum, token);
  }
}




let wartungsweiterleitung = null;

function setWartungstimer(sec) {
  wartungsweiterleitung = setTimeout(function () {
    window.location = "wartung.php";
  }, sec * 1000);
}

function stopRedirect() {
  clearTimeout(wartungsweiterleitung);
  wartungsweiterleitung = null;
}


function hashEmail(email) {
  return crypto.subtle.digest('SHA-256', new TextEncoder().encode(email)).then(hashBuffer => {
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(byte => byte.toString(16).padStart(2, '0')).join('');
    return hashHex;
  });
}





/*
  Function: saveToSessionStorage
    Speichert ein Key-Value-Paar im (flüchtigen) Session-Speicher ab
     
  Parameters:
    key - Schlüssel
    value - Wert
  	
  Returns:
    nichts
*/
function saveToSessionStorage(key, value) {
  if (null != value) {
    window.sessionStorage.setItem(key.toString().trim(), value.toString().trim());
  }
}





/*
  Function: saveToLocalStorage
    Speichert ein Key-Value-Paar im (nicht-flüchtigen) lokalen Speicher ab
     
  Parameters:
    key - Schlüssel
    value - Wert
  	
  Returns:
    nichts
*/
function saveToLocalStorage(key, value) {
  if (null != value) {
    window.localStorage.setItem(key.toString().trim(), value.toString().trim());
  }
}






/*
  Function: getFromSessionStorage
    Liest ein Key-Value-Paar aus dem (flüchtigen) Session-Speicher aus
     
  Parameters:
    key - Schlüssel
  	
  Returns:
    value - Wert
*/
function getFromSessionStorage(key) {
  var result = "";
  try {
    result = window.sessionStorage.getItem(key);
  } catch (e) { }
  return result;
}






/*
  Function: getFromLocalStorage
    Liest ein Key-Value-Paar aus dem (nicht-flüchtigen) lokalen Speicher aus
     
  Parameters:
    key - Schlüssel
  	
  Returns:
    value - Wert
*/
function getFromLocalStorage(key) {
  var result = "";
  try {
    result = window.localStorage.getItem(key);
    if (null == result) {
      result = "";
    }
  } catch (e) { }
  return result;
}






/*
  Function: deleteFromSessionStorage
    Entfernt ein Key-Value-Paar aus dem (flüchtigen) Session-Speicher
     
  Parameters:
    key - Schlüssel
  	
  Returns:
    nichts
*/
function deleteFromSessionStorage(key) {
  window.sessionStorage.removeItem(key);
}






/*
  Function: deleteFromLocalStorage
    Entfernt ein Key-Value-Paar aus dem (nicht-flüchtigen) lokalen Speicher
     
  Parameters:
    key - Schlüssel
  	
  Returns:
    nichts
*/
function deleteFromLocalStorage(key) {
  window.localStorage.removeItem(key);
}






/*
  Function: deleteSessionStorage
    Löscht den (flüchtigen) Session-Speicher
     
  Parameters:
    keine
  	
  Returns:
    nichts
*/
function deleteSessionStorage() {
  window.sessionStorage.clear();
}






/*
  Function: deleteLocalStorage
    Löscht den (nicht-flüchtigen) lokalen Speicher
     
  Parameters:
    keine
  	
  Returns:
    nichts
*/
function deleteLocalStorage() {
  window.localStorage.clear();
}






/*
  Function: deleteStorage
    Löscht den (flüchtigen) Session-Speicher und den (nicht-flüchtigen) lokalen Speicher
     
  Parameters:
    keine
  	
  Returns:
    nichts
*/
function deleteStorage() {
  window.sessionStorage.clear();
  window.localStorage.clear();
}



