class ImageHandler {

    constructor(selector) {
        this.currentIndex = 0;

        this.container = document.getElementById(selector);
        this.images = this.container.getElementsByTagName('img');

        this.informationDiv = document.getElementById(selector + "SliderInformation");

        this.showImage(true)
    }

    showImage(init=false) {
        this.setImageSliderInformation()

        Array.from(this.images).forEach((img, i) => {
            let value;

            if (init){
                value= (i - this.currentIndex) * this.container.clientWidth;
            }
            else{
                value = this.currentIndex * -this.container.clientWidth;
            }

            img.style.transform = `translateX(${value}px)`;
        });
    }
    
    prevImage() {
        this.currentIndex = (this.currentIndex > 0) ? this.currentIndex - 1 : this.images.length - 1;
        this.showImage();
    }

    nextImage() {
        this.currentIndex = (this.currentIndex < this.images.length - 1) ? this.currentIndex + 1 : 0;
        this.showImage();
    }

    setImageSliderInformation(){
        this.informationDiv.textContent = (this.currentIndex + 1) + "/" + this.images.length
    }
}
