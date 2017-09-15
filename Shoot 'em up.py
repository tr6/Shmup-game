###############################################################
#                                                             #
#   Shoot 'em Up Source Code                                  #
#   Author: Tyler Ross                                        #
#   CS 4480 AI                                                #
#   Submitted: 12/12/12                                       #
#                                                             #
#                                                             #
###############################################################



import pygame, random, sys, math
from pygame.locals import *

WINDOWWIDTH = 480
WINDOWHEIGHT = 640
TEXTCOLOR = (255, 255, 255)
BACKGROUNDCOLOR = (0, 0, 0)
FPS = 60
BADDIEMINSIZE = 20
BADDIEMAXSIZE = 40
BADDIEMINSPEED = 1
BADDIEMAXSPEED = 3
BADDIEDODGESPEED = 1
BADDIEBULLETSPEED = 1
BADDIEBULLETRATE = 45
ADDNEWBADDIERATE = 30
BADDIEHEALTH = 300
KAMIKAZEHEALTH = 150
KAMIKAZEMAXSPEED = 4
PLAYERMOVERATE = 3
RAPIDBULLETSPEED = -10
CHARGEBULLETSPEED = 4
STARMINSIZE = 1
STARMAXSIZE = 3
STARMINSPEED = 1
STARMAXSPEED = 6
STARCOLOR = (255, 255, 255)
ADDNEWSTARRATE = 2
LIVES = 5
DEADTIME =  90
INVINCIBILITYTIME = 30


def terminate():
    pygame.quit()
    sys.exit()

def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: # pressing escape quits
                    terminate()
                return

def calculateBulletSpeed():
    bulletSpeed = RAPIDBULLETSPEED
    if moveUp == True and playerRect.top > 0:
        bulletSpeed = RAPIDBULLETSPEED - PLAYERMOVERATE
    if moveDown == True and playerRect.bottom < WINDOWHEIGHT:
        bulletSpeed = RAPIDBULLETSPEED + PLAYERMOVERATE
    return bulletSpeed

def aimBaddieBullet(baddie):
    y = playerRect.top - baddie['rect'].bottom
    x = playerRect.centerx - baddie['rect'].centerx
    if y != 0:
        bulletAim = x/y
        if bulletAim > (BADDIEBULLETSPEED + baddie['speed']):
            return (BADDIEBULLETSPEED + baddie['speed'])
        elif bulletAim < -(BADDIEBULLETSPEED + baddie['speed']):
            return -(BADDIEBULLETSPEED + baddie['speed'])
        return bulletAim
    return 0

def kamikazeCheck(baddie):
    if baddie['health'] <= KAMIKAZEHEALTH:
        return True
    return False

def kamikazeAttack(baddie):
    y = playerRect.top - baddie['rect'].bottom
    x = playerRect.centerx - baddie['rect'].centerx
    if y > 0:
        kamikazeAim = x/y
        if kamikazeAim <= KAMIKAZEMAXSPEED:
            return kamikazeAim
        elif kamikazeAim < -KAMIKAZEMAXSPEED:
            return -KAMIKAZEMAXSPEED
    return KAMIKAZEMAXSPEED
            

def playerHasHitBaddie(playerRect, baddies):
    for b in baddies[:]:
        if playerRect.colliderect(b['rect']):
            createExplosion(b['rect'], explosions)
            baddies.remove(b)
            return True
    return False

def playerHasHitBaddieBullet(playerRect, baddieBullets):
    for b in baddieBullets[:]:
        if playerRect.colliderect(b['rect']):
            baddieBullets.remove(b)
            return True
    return False

def rapidBulletHasHitBaddie(rapidBullet, baddie, score, explosions):
    if rapidBullet['rect'].colliderect(baddie['rect']):
        baddie['health'] -= 10
        rapidBullets.remove(rapidBullet)
        kamikazeCheck(baddie)
        if baddie['health'] <= 0:
            createExplosion(baddie['rect'], explosions)
            baddies.remove(baddie)
            score += 10
    return score

def baddieCrashedIntoBaddie(baddies, explosions, score):
    for b in baddies[:]:
        for c in baddies[:]:
            if b['rect'].colliderect(c['rect']) and (b != c):
                createExplosion(c['rect'], explosions)
                baddies.remove(c)
                score += 10
    return score


def createExplosion(deadEntityRect, explosions):
    newExplosion = {'rect': pygame.Rect(deadEntityRect.left, deadEntityRect.top, deadEntityRect.width, deadEntityRect.height),
                    'surface': pygame.transform.scale(explosionImage, (deadEntityRect.width, deadEntityRect.height)),
                    'frameCounter': 0
                    }
    explosions.append(newExplosion)

def drawText(text, font, surface, x, y):
    textobj = font.render(text, 1, TEXTCOLOR)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# set up pygame, the window, and the mouse cursor
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Shoot \'em up')
pygame.mouse.set_visible(False)

# set up fonts
font = pygame.font.SysFont(None, 48)

# set up images
playerImage = pygame.image.load('playership.png')
playerRect = playerImage.get_rect()
baddieImage = pygame.image.load('baddieship.png')
kamikazeImage = pygame.image.load('baddieship2.png')
rapidBulletImage = pygame.image.load('bulletplaceholder.png')
explosionImage = pygame.image.load('explosion.png')
baddieBulletImage = pygame.image.load('baddiebullet.png')

# show the "Start" screen
windowSurface.blit(pygame.transform.scale(baddieImage, (200, 200)), pygame.Rect(((WINDOWWIDTH / 2) - 100), 30, 200, 200))
drawText('Shoot \'em up', font, windowSurface, (WINDOWWIDTH / 3), 50)
drawText('Controls', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3 + 70))
drawText('W A S D - Move', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3 + 120))
drawText('Spacebar - Shoot', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3 + 170))
drawText('Press a key to start.', font, windowSurface, (WINDOWWIDTH / 3) - 30, (WINDOWHEIGHT / 3) + 250)
pygame.display.update()
waitForPlayerToPressKey()


topScore = 0
while True:
    # set up the start of the game
    baddies = []
    rapidBullets = []
    baddieBullets = []
    explosions = []
    stars = []
    playerLives = LIVES
    score = 0
    moveLeft = moveRight = moveUp = moveDown = False
    playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT - 50)
    playerDead = False #Death flag
    playerInvincible = False #Invincibility Flag
    shootRapid = False
    baddieAddCounter = 0
    starAddCounter = 0
    playerSpawnCounter = 0
    playerInvincibleCounter = 0

    while True: # the game loop runs while the game part is playing

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            #If player is dead and has been for the set time, then they are respawned and the death flag is set to false and the invincibility flag is set to true
            if playerDead and playerSpawnCounter >= DEADTIME:
                    playerSpawnCounter = 0
                    playerDead = False
                    playerInvincible = True
                    playerInvincibleCounter = INVINCIBILITYTIME

            #If player has been invincible for long enough, sets so they aren't invincible anymore
            if playerInvincibleCounter == 0:
                playerInvincible = False

            #Movement Controls
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == ord('a'):
                    moveRight = False
                    moveLeft = True
                if event.key == K_RIGHT or event.key == ord('d'):
                    moveLeft = False
                    moveRight = True
                if event.key == K_UP or event.key == ord('w'):
                    moveDown = False
                    moveUp = True
                if event.key == K_DOWN or event.key == ord('s'):
                    moveUp = False
                    moveDown = True


                #shooting controls
                if event.key == K_SPACE:
                    shootRapid = True

            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                        terminate()

                #More Movement Controls
                if event.key == K_LEFT or event.key == ord('a'):
                    moveLeft = False
                if event.key == K_RIGHT or event.key == ord('d'):
                    moveRight = False
                if event.key == K_UP or event.key == ord('w'):
                    moveUp = False
                if event.key == K_DOWN or event.key == ord('s'):
                    moveDown = False
                if event.key == K_SPACE:
                    shootRapid = False

        # Shoot rapidBullet
        if playerDead == False:
            if shootRapid == True:
                bulletSpeed = calculateBulletSpeed()
                newBullet = {'rect': pygame.Rect((playerRect.centerx - 2), playerRect.top, 4, 6),
                            'speed': bulletSpeed,
                            'surface': rapidBulletImage
                            }
                rapidBullets.append(newBullet)

        #Add stars at top of screen
        starAddCounter += 1
        if starAddCounter == ADDNEWSTARRATE:
            starAddCounter = 0
            starSize = random.randint(STARMINSIZE, STARMAXSIZE)
            newStar = {'rect': pygame.Rect(random.randint(0, WINDOWWIDTH-starSize), 0 - starSize, starSize, starSize),
                        'speed': random.randint(STARMINSPEED, STARMAXSPEED),
                        'color': STARCOLOR
                        }

            stars.append(newStar)


        # Add new baddies at the top of the screen, if needed.
        baddieAddCounter += 1
        if baddieAddCounter == ADDNEWBADDIERATE:
            baddieAddCounter = 0
            baddieSize = random.randint(BADDIEMINSIZE, BADDIEMAXSIZE)
            newBaddie = {'rect': pygame.Rect(random.randint(0, WINDOWWIDTH-baddieSize), 0 - baddieSize, baddieSize, baddieSize),
                        'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                        'surface':pygame.transform.scale(baddieImage, (baddieSize, baddieSize)),
                        'health': BADDIEHEALTH,
                        'shootCounter': BADDIEBULLETRATE - 10,
                        'kamikazeState': False
                        }

            baddies.append(newBaddie)

        #Shoot baddieBullets
        for b in baddies:
            b['shootCounter'] += 1
            if b['shootCounter'] >= BADDIEBULLETRATE and playerDead == False and (b['rect'].bottom < playerRect.top):
                baddieBulletAim = aimBaddieBullet(b)
                newBaddieBullet = {'rect': pygame.Rect(b['rect'].centerx, b['rect'].bottom, 4, 4),
                                   'surface': baddieBulletImage,
                                   'speedx': baddieBulletAim,
                                   'speedy': (BADDIEBULLETSPEED + b['speed']),
                                   }
                baddieBullets.append(newBaddieBullet)
                b['shootCounter'] = 0


        # Move the stars down.
        for s in stars:
            s['rect'].move_ip(0, s['speed'])

        # Move the player around.
        if playerDead == False:
            if moveLeft and playerRect.left > 0:
                playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
            if moveRight and playerRect.right < WINDOWWIDTH:
                playerRect.move_ip(PLAYERMOVERATE, 0)
            if moveUp and playerRect.top > 0:
                playerRect.move_ip(0, -1 * PLAYERMOVERATE)
            if moveDown and playerRect.bottom < WINDOWHEIGHT:
                playerRect.move_ip(0, PLAYERMOVERATE)

        # Move the baddies down.
        for b in baddies[:]:
            b['rect'].move_ip(0, b['speed'])

            #Baddie Bulletdodge
            if shootRapid:
                if b['rect'].centerx > playerRect.centerx and b['rect'].left < playerRect.right:
                    b['rect'].move_ip(BADDIEDODGESPEED, b['speed'])
                if b['rect'].centerx < playerRect.centerx and b['rect'].right > playerRect.left:
                    b['rect'].move_ip(-BADDIEDODGESPEED, b['speed'])
                
            
            #Baddie kamikaze
            if kamikazeCheck(b) and playerDead == False:
                b['surface'] = pygame.transform.scale(kamikazeImage, (b['rect'].width, b['rect'].height))
                kamikazeAim = kamikazeAttack(b)
                if (b['rect'].centerx < playerRect.centerx and b['rect'].centery < playerRect.centery):
                    b['rect'].move_ip(kamikazeAim, KAMIKAZEMAXSPEED)
                elif (b['rect'].centerx > playerRect.centerx and b['rect'].centery < playerRect.centery):
                    b['rect'].move_ip(kamikazeAim, KAMIKAZEMAXSPEED)
                elif (b['rect'].centerx < playerRect.centerx and b['rect'].centery >= playerRect.centery):
                    b['rect'].move_ip(KAMIKAZEMAXSPEED, 0)
                elif (b['rect'].centerx > playerRect.centerx and b['rect'].centery >= playerRect.centery):
                    b['rect'].move_ip(-KAMIKAZEMAXSPEED, 0)
                elif (kamikazeAim < 1 and kamikazeAim > -1):
                    b['rect'].move_ip(0, KAMIKAZEMAXSPEED)
                if (b['rect'].top > playerRect.bottom and b['rect'].centerx > playerRect.left and b['rect'].centerx < playerRect.right):
                    createExplosion(b['rect'], explosions)
                    baddies.remove(b)
                    score += 5




                

        #Check if baddies have crashed
        score = baddieCrashedIntoBaddie(baddies, explosions, score)
                
        #Move the rapidBullets up.
        for r in rapidBullets:
            r['rect'].move_ip(0, r['speed'])

        #Move baddieBullets.
        for d in baddieBullets:
            d['rect'].move_ip(d['speedx'], d['speedy'])

        # Check if any of the baddies have been hit by a bullet.
        for i in rapidBullets[:]:
            for b in baddies[:]:
                score = rapidBulletHasHitBaddie(i, b, score, explosions)

        # Delete baddies that have fallen past the bottom or moved past the sides.
        for b in baddies[:]:
            if b['rect'].top > WINDOWHEIGHT or b['rect'].left > WINDOWWIDTH or b['rect'].right < 0:
                baddies.remove(b)

        # Delete stars that have fallen past the bottom.
        for s in stars[:]:
            if s['rect'].top > WINDOWHEIGHT:
                stars.remove(s)

        #Delete rapidBullets that have flown past the top
        for r in rapidBullets[:]:
            if r['rect'].bottom < 0:
                rapidBullets.remove(r)

        #Delete baddieBullets that have moved out of screen
        for d in baddieBullets[:]:
            if d['rect'].top > WINDOWHEIGHT or d['rect'].left > WINDOWWIDTH or d['rect'].right < 0:
                baddieBullets.remove(d)

        # Draw the game world on the window.
        windowSurface.fill(BACKGROUNDCOLOR)

        #Draw each star
        for s in stars:
            pygame.draw.rect(windowSurface, s['color'], s['rect'])

        # Draw the player's rectangle
        if playerDead == False:
            windowSurface.blit(playerImage, playerRect)

        # Draw each baddie
        for b in baddies:
            windowSurface.blit(b['surface'], b['rect'])
            
        # Draw each rapidbullet
        for b in rapidBullets:
            windowSurface.blit(rapidBulletImage, b['rect'])
            
        #Check if player died
        if playerDead == False and playerInvincible == False:
             if playerHasHitBaddie(playerRect, baddies) or playerHasHitBaddieBullet(playerRect, baddieBullets):
                playerLives -= 1
                playerDead = True
                playerSpawnCounter = 0
                createExplosion(playerRect, explosions)
                playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT - 50)
                

        #Remove explosions that have been around too long
        for e in explosions[:]:
            e['frameCounter'] += 1
            if e['frameCounter'] >= 11:
                explosions.remove(e)

        #Draw each explosion
        for e in explosions:
            windowSurface.blit(e['surface'], e['rect'])

        #Draw baddiebullet
        for d in baddieBullets:
            windowSurface.blit(d['surface'], d['rect'])
            
        # Draw the score and top score.
        drawText('Score: %s' % (score), font, windowSurface, 10, 0)
        drawText('Top Score: %s' % (topScore), font, windowSurface, 10, 40)
        drawText('Lives: %s' % (playerLives), font, windowSurface, 10, 80)

        #Counts up when player is dead
        if playerSpawnCounter < DEADTIME:
            playerSpawnCounter += 1

        #Counts down after play has been respawned so that are invincible for a short time
        if playerInvincibleCounter > 0:
            playerInvincibleCounter -= 1

        pygame.display.update()

        # Check for Game Oover
        if playerLives <= 0:
            if score > topScore:
                topScore = score # set new top score
            break
            

        mainClock.tick(FPS)

    # Stop the game and show the "Game Over" screen.

    drawText('GAME OVER', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
    drawText('Press a key to play again.', font, windowSurface, (WINDOWWIDTH / 3) - 80, (WINDOWHEIGHT / 3) + 50)
    pygame.display.update()
    waitForPlayerToPressKey()
