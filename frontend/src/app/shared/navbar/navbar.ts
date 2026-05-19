import { Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class Navbar implements OnDestroy {
  isCollapsed = false;

  constructor(private router: Router) {}

  toggleCollapsed(): void {
    this.isCollapsed = !this.isCollapsed;
    document.body.classList.toggle('sidebar-collapsed', this.isCollapsed);
  }

  logout(): void {
    this.router.navigate(['/']);
  }

  reportIssue(): void {
    alert('Funcionalidad de reportar problema próximamente disponible.');
  }

  ngOnDestroy(): void {
    document.body.classList.remove('sidebar-collapsed');
  }
}