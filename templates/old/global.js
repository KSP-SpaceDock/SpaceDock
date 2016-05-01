{% raw %}
(function() {
  var box, createCookie, donation_alert, fn, i, j, k, len, len1, len2, link, readCookie, ref, ref1, ref2;

  if ($(".dropdown-toggle").length > 0) {
    $(".dropdown-toggle").dropdown();
  }

  ref = document.querySelectorAll('.upload-well');
  fn = function(box) {
    var down, input, link, progress, startX, startY, x, y;
    link = box.querySelector('a');
    input = box.querySelector('input');
    progress = box.querySelector('.upload-progress');
    if (box.dataset.file != null) {
      input = document.getElementById(box.dataset.file);
    }
    link.addEventListener('click', function(e) {
      e.preventDefault();
      return input.click();
    }, false);
    input.addEventListener('change', function(e) {
      progress.style.width = 0;
      progress.classList.remove('fade-out');
      return eval(box.dataset.event + '(input.files, box)');
    }, false);
    progress.addEventListener('animationend', function(e) {
      progress.style.width = 0;
      return progress.classList.remove('fade-out');
    }, false);
    if (box.classList.contains('scrollable')) {
      down = false;
      startX = startY = x = y = 0;
      box.addEventListener('mousedown', function(e) {
        var _x, _y;
        _x = box.style.backgroundPosition.split(' ')[0];
        _y = box.style.backgroundPosition.split(' ')[1];
        x = parseInt(_x.substr(0, _x.length - 2));
        y = parseInt(_y.substr(0, _y.length - 2));
        startX = e.clientX;
        startY = e.clientY;
        return down = true;
      }, false);
      box.addEventListener('mouseup', function(e) {
        return down = false;
      }, false);
      return box.addEventListener('mousemove', function(e) {
        var _x, _y;
        if (down) {
          _x = e.clientX - (startX - x);
          _y = e.clientY - (startY - y);
          if (box.dataset.scrollX == null) {
            _x = 0;
          }
          if (box.dataset.scrollY == null) {
            _y = 0;
          }
          box.style.backgroundPosition = _x + "px " + _y + "px";
          if (box.dataset.scrollX != null) {
            $('#' + box.dataset.scrollX).val(_x);
          }
          if (box.dataset.scrollY != null) {
            return $('#' + box.dataset.scrollY).val(_y);
          }
        }
      }, false);
    }
  };
  for (i = 0, len = ref.length; i < len; i++) {
    box = ref[i];
    fn(box);
  }

  ref1 = document.querySelectorAll('.follow-button, .unfollow-button');
  for (j = 0, len1 = ref1.length; j < len1; j++) {
    link = ref1[j];
    link.addEventListener('click', function(e) {
      var follow, xhr;
      e.preventDefault();
      xhr = new XMLHttpRequest();
      follow = false;
      if (e.target.classList.contains('follow-button')) {
        xhr.open('POST', "/mod/" + e.target.dataset.mod + "/follow");
        e.target.classList.remove('follow-button');
        e.target.classList.add('unfollow-button');
        e.target.textContent = 'Unfollow';
        follow = true;
      } else {
        xhr.open('POST', "/mod/" + e.target.dataset.mod + "/unfollow");
        e.target.classList.remove('unfollow-button');
        e.target.classList.add('follow-button');
        e.target.textContent = 'Follow';
      }
      xhr.onload = function() {
        var error;
        try {
          JSON.parse(this.responseText);
          if (follow) {
            return document.getElementById('alert-follow').classList.remove('hidden');
          }
        } catch (error) {
          return window.location.href = '/register';
        }
      };
      return xhr.send();
    }, false);
  }

  ref2 = document.querySelectorAll('.feature-button, .unfeature-button');
  for (k = 0, len2 = ref2.length; k < len2; k++) {
    link = ref2[k];
    link.addEventListener('click', function(e) {
      var xhr;
      e.preventDefault();
      xhr = new XMLHttpRequest();
      if (e.target.classList.contains('feature-button')) {
        xhr.open('POST', "/mod/" + e.target.dataset.mod + "/feature");
        e.target.classList.remove('feature-button');
        e.target.classList.add('unfeature-button');
        e.target.textContent = 'Unfeature';
      } else {
        xhr.open('POST', "/mod/" + e.target.dataset.mod + "/unfeature");
        e.target.classList.remove('unfeature-button');
        e.target.classList.add('feature-button');
        e.target.textContent = 'Feature';
      }
      return xhr.send();
    }, false);
  }

  readCookie = function(name) {
    var c, ca, l, len3, nameEQ;
    nameEQ = name + "=";
    ca = document.cookie.split(';');
    for (l = 0, len3 = ca.length; l < len3; l++) {
      c = ca[l];
      while (c.charAt(0) === ' ') {
        c = c.substring(1, c.length);
      }
      if (c.indexOf(nameEQ) === 0) {
        return c.substring(nameEQ.length, c.length);
      }
    }
    return null;
  };

  window.readCookie = readCookie;

  createCookie = function(name, value, days) {
    var date, expires;
    if (days) {
      date = new Date();
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
      expires = "; expires=" + date.toGMTString();
    } else {
      expires = "; expires=session";
    }
    return document.cookie = name + "=" + value + expires + "; path=/";
  };

  window.createCookie = createCookie;

  createCookie('first_visit', 'false', 365 * 10);

  $('a[data-scroll]').click(function(e) {
    var target;
    e.preventDefault();
    target = e.target;
    if (e.target.tagName !== 'A') {
      target = e.target.parentElement;
    }
    return $('html, body').animate({
      scrollTop: $(target.hash).offset().top - 20
    }, 1500);
  });

  donation_alert = document.querySelector("#alert-donate > button.close");

  if (donation_alert) {
    donation_alert.addEventListener('click', function(e) {
      return createCookie('dismissed_donation', 'true');
    }, false);
  }

}).call(this);
{% endraw %}