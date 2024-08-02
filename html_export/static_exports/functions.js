const imageHandler = {};


class ImageHandler {

    constructor(selector) {
        this.currentIndex = 0;

        this.container = document.getElementById(selector);
        this.images = this.container.getElementsByTagName('img');

        this.informationDiv = document.getElementById(selector + "SliderInformation");

        this.showImage(true)

        window.addEventListener('resize', () => this.showImage(true));
    }

    showImage(init=false) {
        this.setImageSliderInformation()

        // Ensure all images are loaded before calculating dimensions
        const imagesLoadedPromises = Array.from(this.images).map(img => {
            return new Promise(resolve => {
                if (img.complete) {
                    resolve();
                } else {
                    img.onload = resolve;
                }
            });
        });

        Promise.all(imagesLoadedPromises).then(() => {

            Array.from(this.images).forEach((img, i) => {
                let value;
                console.log(`${img.x} ${img.clientX} ${img.x1}`)

                if (init) {
                    value = ((i - this.currentIndex) * this.container.clientWidth) + ((this.container.clientWidth - img.clientWidth) / 2);
                } else {
                    const padding = (this.container.clientWidth - img.clientWidth) * i  + ((this.container.clientWidth - img.clientWidth) / 2);
                    //console.log(`${i} ${this.container.clientWidth} ${img.clientWidth} ${padding}`)
                    value = (this.currentIndex * -this.container.clientWidth) + (padding);
                }

                img.style.transform = `translateX(${value}px)`;
            });

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

function addImageHandler(imageHandlerSelectorName) {
    document.addEventListener('DOMContentLoaded', (event) => {
        imageHandler[imageHandlerSelectorName] = new ImageHandler(imageHandlerSelectorName);
    });
}

function filter_export(name, element){
    const buttons = document.querySelectorAll('.export_filter > div[type="filter"]');
    buttons.forEach(function(button) {
        button.classList.remove('active');
    });

    element.classList.add('active');

    document.querySelectorAll('div[type="finance_model"]').forEach(
        (div) => {
            div.style.display = 'none'
        });

    document.getElementById(name).style.display = 'block';
}