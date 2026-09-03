function hideAllSections() {
    const sections = document.querySelectorAll('.section');
    sections.forEach(function (section) {
        section.classList.remove('active-section');
    });
}

function showSection(sectionId) {
    hideAllSections();
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active-section');
        if (window.location.hash !== '#' + sectionId) {
            window.location.hash = sectionId;
        }
    }
    if (window.jQuery) {
        $('.navbar-collapse').collapse('hide');
    }
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

function goHome() {
    showSection('home');
}

function goAbout() {
    showSection('about');
}

function goAdmissions() {
    showSection('admissions');
}

function goPrograms() {
    showSection('programs');
}

function goContact() {
    showSection('contact');
}

document.addEventListener('DOMContentLoaded', function () {
    const initialSection = window.location.hash ? window.location.hash.substring(1) : 'home';
    showSection(initialSection);
});

//admin section

(function () {
    var navLinks = document.querySelectorAll(".nav-link");
    var sections = document.querySelectorAll(".content-section");
    var adminLoginForm = document.getElementById("admin-login-form");
    var adminLoginStatus = document.getElementById("admin-login-status");
    var applicantFilterForm = document.getElementById("applicant-filter-form");
    var clearApplicantFilterButton = document.getElementById("clear-applicant-filter");
    var studentFilterForm = document.getElementById("student-filter-form");
    var clearStudentFilterButton = document.getElementById("clear-student-filter");

    function showSection(sectionId) {
        sections.forEach(function (section) {
            section.classList.toggle("active-section", section.id === sectionId);
        });

        navLinks.forEach(function (link) {
            link.classList.toggle("active", link.getAttribute("data-target") === sectionId);
        });
    }

    navLinks.forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            var sectionId = link.getAttribute("data-target");
            showSection(sectionId);

            var mobileSidebar = document.getElementById("mobileSidebarNav");
            if (mobileSidebar && mobileSidebar.classList.contains("in")) {
                window.jQuery(mobileSidebar).collapse("hide");
            }
        });
    });

    if (applicantFilterForm) {
        applicantFilterForm.addEventListener("submit", function () {
            applicantFilterForm.action = window.location.pathname + "#appication";
        });
    }

    if (clearApplicantFilterButton) {
        clearApplicantFilterButton.addEventListener("click", function () {
            window.location.href = window.location.pathname + "#appication";
        });
    }

    if (studentFilterForm) {
        studentFilterForm.addEventListener("submit", function () {
            studentFilterForm.action = window.location.pathname + "#allstudent";
        });
    }

    if (clearStudentFilterButton) {
        clearStudentFilterButton.addEventListener("click", function () {
            window.location.href = window.location.pathname + "#allstudent";
        });
    }

}());

//chatbot

document.addEventListener("DOMContentLoaded", function () {

    const chatbotButton = document.getElementById("chatbotButton");
    const chatbotWindow = document.getElementById("chatbotWindow");
    const chatbotClose = document.getElementById("chatbotClose");
    const chatbotInput = document.getElementById("chatbotInput");
    const chatbotSend = document.getElementById("chatbotSend");
    const chatbotMessages = document.getElementById("chatbotMessages");
    const chatOptions = document.querySelectorAll(".chat-option");

    chatbotButton.addEventListener("click", function () {
        chatbotWindow.style.display = "flex";
        chatbotInput.focus();
    });

    chatbotClose.addEventListener("click", function () {
        chatbotWindow.style.display = "none";
    });

    function addMessage(message, type) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add(type + "-message");
        messageDiv.textContent = message;
        chatbotMessages.appendChild(messageDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function sendMessage() {
        const message = chatbotInput.value.trim();
        if (message === "") {
            return;
        }

        addMessage(message, "user");
        chatbotInput.value = "";

        fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        })

        .then(response => response.json())
        .then(data => {
            addMessage(data.reply, "bot");
        })
        .catch(error => {
            console.error("Error:", error);
            addMessage(
                "Sorry, something went wrong. Please try again.",
                "bot"
            );
        });
    }

    chatbotSend.addEventListener("click", function () {
        sendMessage();
    });

    chatbotInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    chatOptions.forEach(function (button) {
        button.addEventListener("click", function () {
            const question = button.textContent.trim();
            chatbotInput.value = question;
            sendMessage();
        });
    });
});
