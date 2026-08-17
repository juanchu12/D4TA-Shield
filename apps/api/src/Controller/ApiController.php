<?php

namespace App\Controller;

use App\Entity\User;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpKernel\Exception\AccessDeniedHttpException;

abstract class ApiController extends AbstractController
{
    protected function getAppUser(): User
    {
        $user = $this->getUser();
        if (!$user instanceof User) {
            throw new AccessDeniedHttpException('Authentication required.');
        }

        if (!$user->isActive() || $user->getTenant() === null || !$user->getTenant()->isActive()) {
            throw new AccessDeniedHttpException('Inactive user or tenant.');
        }

        return $user;
    }
}
