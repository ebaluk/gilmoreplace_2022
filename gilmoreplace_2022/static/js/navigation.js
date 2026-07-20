$(function () {
  
  let pageTop = 0,
      atTop = true,
      showPopup = false;
  
  
    hideMenuBox = function() {
      //sessionStorage.setItem("showMenuBox", false);
      //let storedBoolean = JSON.parse(sessionStorage.getItem("showMenuBox"));
      //this.App.showMenuBox = storedBoolean;
      // scroll to form
      setTimeout(() => {        
        window.scrollTo(0, window.innerHeight);        
      }, 100);
    };
    
    handleMenu = function() {
      showMenu = true;
    };

    handleClickRegisterMobile = function() {
      setTimeout(() => {      
        window.scrollTo(0, window.innerHeight * 0.85);
      }, 100);
    };

    handleScroll = function() {
      let windowScroll = window.pageYOffset;

      if (windowScroll < 1) {
          $('#app>nav').addClass('atTop');
        // this.$refs.nav.classList.add('atTop')
        // atTop = true;
        // this.App.showNav = false;
      } else if (windowScroll > this.pageTop) {
        // downscroll code
        // this.$refs.nav.classList.add('top')
        this.atTop = false;
        this.App.showNav = false;
      } else {
        // upscroll code
        // this.$refs.nav.classList.add('top')
        this.App.showNav = true;
      }
      this.pageTop = windowScroll;
    },
    togglePopup() {
      this.showPopup = !this.showPopup;
    }
  },
  destroyed() {
    window.removeEventListener("scroll", this.handleScroll);
  },
  created() {
    window.addEventListener("scroll", this.handleScroll);
  }
};
});