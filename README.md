# VRChat Haptic Pancake (for trackers)
A dirt cheap solution to enable haptic feedback on the vive (and other OpenVR compatible) trackers

![Promo picture that demonstrates how it works](Images/promo.png)

# Prerequisites

1. Access to a 3D printer (or a 3D printer service)
2. A vibration motor for each tracker. I recommend [this one.](https://www.aliexpress.com/item/1005004653448729.html "Link to Aliexpres")

# Guide
1. Let's 3D print the pancake! You can use any material, but using a TPU will grand an extra dampening effect what can improve your tracking.
2. Put the motor inside. If it feels lose, use a bit of duct tape on the side.

![Promo picture that demonstrates how it works](Images/pancake.png)

3. Attach the cables accoring to the image. Push the pogo pins a bit down with one finger and snap the cable inside its locking mechanism.

![Promo picture that demonstrates how it works](Images/cable.png)

4. Screw back the tracker on the strap

![Promo picture that demonstrates how it works](Images/sandwitch.png)

5. Prepare your avatar by adding VRC Contact Receiver component to each bone you wear your tracker on.  
    * Ensure that it has been positioned properly and only the "Allow Others" is enabled in the Filtering settings.
    * Feel free to define which collision tags will trigger your haptics by adding the specific collision tags.
    * Set the Receiver Type to Proximity (This is the only supported type for now in the bridge app)
    * Come up with a good unique name for the parameter. For example 'LeftFootTouched' if you want to trigger the haptics in the tracker on your left foot. The name itself can be whatever and it does not really matter as long as you get it right everywhere.

![Promo picture that demonstrates how it works](Images/unity.png)

6. Add the parameters you've assigned to the Contact Receivers in the previous step to your Avatar's parameters.

![Promo picture that demonstrates how it works](Images/params.png)

8. Upload your avatar
9. If you are updating an existing avatar, be sure to clear your `AppData\LocalLow\VRChat\VRChat\OSC\` directory. Or else VRChat won't recognise the new parameter.

![Promo picture that demonstrates how it works](Images/bridgeapp.png)

10. Run the bridge app, match the trackers with the declared parameters. You can press the 'Test' button to send them a short vibration. Note that the app requires SteamVR running in the background.
11. Enjoy and have fun!

# Feature Plan
- Per tracker intensity setting
- Haptic Feedback cooldown and trigger patterns
- Support for DIY haptic devices through serial connection

# Special Thanks
- @BubblegumFoxxo (For helping in the testing and debugging)
- @vulp_vibes (for giving me the idea)
