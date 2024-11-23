# VRChat Haptic Pancake (for trackers)
A dirt cheap solution to enable haptic feedback on the Vive trackers in VRChat and Resonite.

[<img src="Images/promo.png">](https://youtu.be/c1JQpJwJ7_c)

# Contact

Curious about the development? Have any questions? Join the discord!

[![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/DEWbQHqbRS)

# How to make
[> Check out the Wiki for a full guide! <](https://github.com/Z4urce/VRC-Haptic-Pancake/wiki)

# Planned Features
- Support for DIY haptic devices through serial connection

# Frequently Asked Questions
- Will this harm my tracker in any way?
   - The tracking capabilities of your tracker should not get harmed at all. In case of an unexpected high load the output pin of your tracker might get fried out. That only means that in the worst case scenario you won't be able to use a vibration function on that particular tracker anymore. However after two weeks of intensive testing on my own trackers I experienced no problems whatsoever. I'll update this page if anything changes.
- Will this affect my tracking?
   - Since I implemented the vibration pattern system, it barely affects the tracking. But it still depends on the selected pattern. For example You should experience minor to no drifting with the 'Linear' one.
- Can I put the tracker elsewhere after setting up my avatar?
   - Yes. None of the trackers are permanently linked to any parts of your avatar. In fact you can even hotswap them. Just ensure you are using the right parameters in the bridge app. 
- How does this work with non-Vive trackers?
   - The software side support is guaranteed by the Haptic Pancake Bridge app. Every SteamVR compatible tracker will be recognized and external device support is imminent.
   - The hardware side is a bit more complicated:
       - For Tundra trackers you will need a custom PCB from here: [Tundra Tapper](https://github.com/nkotech/Tundra-Tapper)
       - Controllers that has been re-programmed into trackers will just work as they have haptics built in.
       - Anything else should only work if the hardware respects the SteamVR api and has built in haptics or IO to attach one.

# Support the project
<a href='https://ko-fi.com/Z4urce' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' />

# Special Thanks
- @BubblegumFoxxo (For helping in the testing and debugging)
- @vulp_vibes (for giving me the idea)
