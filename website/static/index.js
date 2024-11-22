document.addEventListener("DOMContentLoaded", () => {
  const toggleButton = document.getElementById("navbar__toggle");
  const navbarMenu = document.getElementById("navbar__menu");

  if (toggleButton) {
    toggleButton.addEventListener("click", () => {
      navbarMenu.classList.toggle("active");
    });
  }

  const closeButtons = document.querySelectorAll(".alert .close");

  closeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const alertBox = button.parentElement;
      alertBox.style.opacity = "0";
      setTimeout(() => {
        alertBox.style.display = "none";
      }, 300);
    });
  });
});
