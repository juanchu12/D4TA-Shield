<?php

namespace App\Command;

use App\Entity\Tenant;
use App\Entity\User;
use App\Repository\TenantRepository;
use App\Repository\UserRepository;
use Symfony\Component\Console\Attribute\AsCommand;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

#[AsCommand(name: 'app:seed-demo', description: 'Seed demo tenant and users for D4TA Shield')]
final class SeedDemoCommand extends Command
{
    public function __construct(
        private readonly TenantRepository $tenants,
        private readonly UserRepository $users,
        private readonly UserPasswordHasherInterface $hasher,
        private readonly string $projectDir,
    ) {
        parent::__construct();
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);

        $tenant = $this->tenants->findBySlug('demo') ?? (new Tenant())
            ->setName('Demo Legal')
            ->setSlug('demo');
        $this->tenants->save($tenant);

        $accounts = [
            ['admin@demo.d4ta.local', 'admin123', [User::ROLE_ADMIN, User::ROLE_LEGAL]],
            ['legal@demo.d4ta.local', 'legal123', [User::ROLE_LEGAL]],
            ['comercial@demo.d4ta.local', 'comercial123', [User::ROLE_COMERCIAL]],
            ['readonly@demo.d4ta.local', 'readonly123', [User::ROLE_READONLY]],
        ];

        foreach ($accounts as [$email, $password, $roles]) {
            $existing = $this->users->findOneBy(['email' => $email]);
            $user = $existing ?? (new User())->setEmail($email)->setTenant($tenant);
            $user->setRoles($roles);
            $user->setPassword($this->hasher->hashPassword($user, $password));
            $this->users->save($user);
            $io->writeln(sprintf('  %s / %s', $email, $password));
        }

        $io->success('Demo tenant "demo" seeded. Login with any account above.');

        return Command::SUCCESS;
    }
}
