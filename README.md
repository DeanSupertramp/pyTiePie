<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/DeanSupertramp/pyTiePie">
    <img src="images/logo_dimes.png" alt="Logo" width="438" height="192">
  </a>

<h3 align="center">pyTiePie</h3>

  <p align="center">
    Project for Master's Degree Thesis in Electronics Engineering
    <br />
    <a href="https://github.com/DeanSupertramp/pyTiePie"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/DeanSupertramp/pyTiePie">View Demo</a>
    ·
    <a href="https://github.com/DeanSupertramp/pyTiePie/issues">Report Bug</a>
    ·
    <a href="https://github.com/DeanSupertramp/pyTiePie/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<!-- 
[![Product Name Screen Shot][product-screenshot]](https://example.com) -->

<!-- Here's a blank template to get started: To avoid retyping too much info. Do a search and replace with your text editor for the following: `DeanSupertramp`, `pyTiePie`, `DeanSupertramp`, `andrea-alecce`, `gmail`, `andrealecce3`, `project_title`, `project_description` -->

Project for Master's Degree Thesis in Electronics Engineering.
Università della Calabria


<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

<!-- * [Next.js](https://nextjs.org/)
* [React.js](https://reactjs.org/)
* [Vue.js](https://vuejs.org/)
* [Angular](https://angular.io/)
* [Svelte](https://svelte.dev/)
* [Laravel](https://laravel.com)
* [Bootstrap](https://getbootstrap.com)
* [JQuery](https://jquery.com) -->


* [Python3](https://www.python.org/)
* [TiePie](https://www.tiepie.com/en)
* [LTSpice](https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html)
* and other future tools...

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is a list of things you need for use the software and how to install them.
1. Python3
2. Driver and software of TiePie (mod. HS5) at: [https://www.tiepie.com/en/usb-oscilloscope/handyscope-hs5#downloads](https://www.tiepie.com/en/usb-oscilloscope/handyscope-hs5#downloads)
3. Install the Python bindings by executing: 
    ```sh
    pip install python-libtiepie
    ```
    more information [here](https://www.tiepie.com/en/libtiepie-sdk/python).

4. Install packages:
   ```sh
   pip install pandas
   ```
   or
   ```sh
   conda install pandas
   ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/DeanSupertramp/pyTiePie.git
   ```

<p align="right">(<a href="#top">back to top</a>)</p>

### Map of the repository
* [project](https://github.com/DeanSupertramp/pyTiePie/tree/main/project): contains scripts written to work with TiePie.
* [libtiepie](https://github.com/DeanSupertramp/pyTiePie/tree/main/libtiepie): TiePie's Python module.
* [example](https://github.com/DeanSupertramp/pyTiePie/tree/main/examples): contains example for TiePie.
* [images](https://github.com/DeanSupertramp/pyTiePie/tree/main/images): contains images useful for the repository.
* [utils](https://github.com/DeanSupertramp/pyTiePie/tree/main/utils): contains scripts, tools and simulations:
  * [Excel](https://github.com/DeanSupertramp/pyTiePie/tree/main/utils/Excell) files
  * [Spice](https://github.com/DeanSupertramp/pyTiePie/tree/main/utils/Spice_Circuit): LTSpice simulation files
  * [script](https://github.com/DeanSupertramp/pyTiePie/tree/main/utils/script): Python script for simulation and analysis.  

<!-- USAGE EXAMPLES -->
<!-- ## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#top">back to top</a>)</p>
 -->


<!-- ROADMAP -->
## Roadmap

- [ ] Circuit sensitivity analysis respect to a capacity variation, simulating the use of an ADC for acquisition
  - [x] Impedance measurement with R series
  - [x] Calculate the voltage difference measured for a given variation in capacitance
  - [x] Simulate the quantization of the ADC
  - [ ] Apply lock-in
  - [ ] Derive the phasors at the various frequencies and therefore dC at the various frequencies by comparing the estimated dC with the theoretical simulated one
- [ ] Impedance measurement with Wheatstone bridge
  - [ ] Simulate both the reference capacitor on a healthy point and in the air
  - [ ] Repeat the analysis for the estimate of dC

See the [open issues](https://github.com/DeanSupertramp/pyTiePie/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->
<!-- ## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>
 -->


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@DeanSupertramp](https://twitter.com/DeanSupertramp) - andrealecce3@gmail.com

Project Link: [https://github.com/DeanSupertramp/pyTiePie](https://github.com/DeanSupertramp/pyTiePie)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/DeanSupertramp/pyTiePie.svg?style=for-the-badge
[contributors-url]: https://github.com/DeanSupertramp/pyTiePie/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/DeanSupertramp/pyTiePie.svg?style=for-the-badge
[forks-url]: https://github.com/DeanSupertramp/pyTiePie/network/members
[stars-shield]: https://img.shields.io/github/stars/DeanSupertramp/pyTiePie.svg?style=for-the-badge
[stars-url]: https://github.com/DeanSupertramp/pyTiePie/stargazers
[issues-shield]: https://img.shields.io/github/issues/DeanSupertramp/pyTiePie.svg?style=for-the-badge
[issues-url]: https://github.com/DeanSupertramp/pyTiePie/issues
[license-shield]: https://img.shields.io/github/license/DeanSupertramp/pyTiePie.svg?style=for-the-badge
[license-url]: https://github.com/DeanSupertramp/pyTiePie/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/andrea-alecce
[product-screenshot]: images/screenshot.png
