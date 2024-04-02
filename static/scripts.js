// On ready
$(document).ready(function ()
{
    // Normalize the URL
    window.history.replaceState({}, document.title, window.location.pathname);

    // Fade out the alert if it exists
    $('#alert').fadeTo(5000, 500).slideUp(500, function ()
    {
        $('#alert').slideUp(500);
    });
});

// Toggle color mode
document.getElementById('btnToggleColorMode').addEventListener('click',()=>{
    if (document.documentElement.getAttribute('data-bs-theme') == 'dark')
    {
        document.documentElement.setAttribute('data-bs-theme','light')
    }
    else
    {
        document.documentElement.setAttribute('data-bs-theme','dark')
    }
});