# release-terraform-integration
This container based integration uses Digital.ai Python SDK.

The development of a plugin is currently underway.

### Build and Publish

* Configure the plugin and registry details in the **project.properties**
* Update the Release server details in **.xebialabs/config.yaml**
* Open a command prompt and navigate to the root directory of project.
* Unix/macOS  
  * Builds the zip, image and pushes the image to the configured registry  
  ``` sh build.sh ``` 
  * Builds the zip  
  ``` sh build.sh --zip ``` 
  * Builds the image and pushes the image to the configured registry  
   ```  sh build.sh --image ```
  * Builds the zip, creates image, pushes the image to the configured registry, and uploads the zip to the release server  
   ```  sh build.sh --upload ```
* Windows  
  * Builds the zip, image and pushes the image to the configured registry  
  ``` build.bat ``` 
  * Builds the zip  
  ``` build.bat --zip ``` 
  * Builds the image and pushes the image to the configured registry  
  ``` build.bat --image ```
  * Builds the zip, creates image, pushes the image to the configured registry, and uploads the zip to the release server  
  ``` build.bat --upload ```