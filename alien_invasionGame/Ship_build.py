import sys
import pygame


class AlienInvasion:
    """Overall Class to manage game assest and behavior"""
    def __init__(self):
        """Initialize the game and create the game resources"""
        self.screen=pygame.display.set.mode((1200,800))
        pygame.display.set_caption("Alien Invasion")


        