#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist

import time
import lcm
from fearing import xbox_joystick_state
from fearing import header

lcm_addr = rospy.get_param('lcm_addr', 'udpm://239.255.76.67:7667?ttl=1')
lcm_robot_id = rospy.get_param('lcm_robot_id','/999')
lcm_topic = lcm_robot_id + '/joy'

lc = None
joy_msg = xbox_joystick_state()
joy_msg.header = header()
joy_msg.header.seq = 0
joy_msg.header.time = time.time()
joy_msg.axes = 6*[0]
joy_msg.buttons = 12*[0]

def ros_to_zumy_lcm(data):
  global joy_msg

  v_cmd = data.linear.x
  o_cmd = data.angular.z

  rospy.loginfo('Read (v,o)=(%f,%f) on ROS:cmd_vel at %s' % (v_cmd, o_cmd, rospy.get_time()))
  
  if v_cmd < -1.0:
    v_cmd = -1.0
  if v_cmd > 1.0:
    v_cmd = 1.0
  if o_cmd < -1.0:
    o_cmd = -1.0
  if o_cmd > 1.0:
    o_cmd = 1.0

  r_cmd = (v_cmd + o_cmd)/2
  l_cmd = (v_cmd - o_cmd)/2

  joy_msg.header.time = time.time()
  joy_msg.header.seq += 1
  joy_msg.axes = [0, -l_cmd, 0, 0, -r_cmd, 0]
  lc.publish(lcm_topic, joy_msg.encode())
  rospy.loginfo('Sent (r,l)=(%f,%f) on LCM:%s at %s' % (r_cmd, l_cmd, 
    lcm_topic, joy_msg.header.time))

def listener():
  global lc
  while lc is None:
      try:
          lc = lcm.LCM(lcm_addr)
      except RuntimeError as e:
          print("couldn't create LCM:" + str(e))
          time.sleep(1)
  print("LCM connected properly!")
  print("LCM running...")

  rospy.init_node('zumy_lcb_sub', anonymous=True)
  rospy.Subscriber('cmd_vel', Twist, ros_to_zumy_lcm)
  rospy.spin()

if __name__ == '__main__':
  listener()
