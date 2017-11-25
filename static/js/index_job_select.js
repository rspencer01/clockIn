document.addEventListener('DOMContentLoaded', function () {
  document.querySelector('select[name="job"]').onchange = changeJob;
}, false);

function changeJob(event) {
  if (event.target.value === 'None') {
    window.location.href = '/';
    return;
  }

  document.querySelector('form[name="job_select_form"]').submit();
}
